"""
Course titles from cosmo export are loaded into chroma collection.
Getter functions are provided to get course titles from chroma collection.
This is primarily for fuzzy matching course titles for Get.py.

NOTE: Chroma needs to be running on port 8001. This code defaults to localhost.
On Caruana:
```bash
chroma run --port 8001 --path /home/bianders/Databases/chroma
```
"""

# Imports are heavy and noisy. We want a spinner and to suppress all noisy torch/tensorflow output.
# This is entirely due to SentenceTransformers and the rerankers library.
# -----------------------------------------------------------------
from rich.console import Console
from contextlib import contextmanager
import os
import logging
import warnings
from rich.progress import Progress
import asyncio


# The nuclear option: shut the entire computer up
@contextmanager
def silence_all_output():
    """
    Context manager that completely silences both stdout and stderr by redirecting to /dev/null at the OS level.
    """
    # Save original file descriptors
    old_stdout = os.dup(1)
    old_stderr = os.dup(2)

    # Close and redirect stdout and stderr
    os.close(1)
    os.close(2)
    os.open(os.devnull, os.O_WRONLY | os.O_CREAT)
    os.dup2(1, 2)  # Redirect stderr to the same place as stdout

    try:
        yield
    finally:
        # Restore original stdout and stderr
        os.dup2(old_stdout, 1)
        os.dup2(old_stderr, 2)
        os.close(old_stdout)
        os.close(old_stderr)


# Silence warnings moving forward
warnings.filterwarnings("ignore")
# Suppress various logging messages
logging.basicConfig(level=logging.ERROR)

# our imports
# -----------------------------------------------------------------
console = Console(width=100)  # for spinner

with silence_all_output():
    with console.status("[green]Loading...", spinner="dots"):
        import sys, re, html, asyncio, chromadb
        from pathlib import Path
        import pandas as pd
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction  # type: ignore
        from chromadb.api.models.AsyncCollection import AsyncCollection
        from chromadb.api import AsyncClientAPI

        # Why load this here? Because it's needed in the rerank function, and we want to silence it.
        from rerankers import Reranker  # type: ignore
        from Kramer import get_course_title
        import subprocess
        import platform
        from typing import Literal

# Now that we've imported these libraries, we can set the logging levels.
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("pytorch_transformers").setLevel(logging.ERROR)


# Two import config functions
def detect_device() -> Literal["cuda", "mps", "cpu"]:
    """
    Detect available hardware acceleration for tensor operations without importing torch.
    Returns 'cuda', 'mps', or 'cpu' based on what's available.
    """
    # Check for CUDA GPUs
    try:
        # Try to use nvidia-smi command to detect NVIDIA GPUs
        result = subprocess.run(
            ["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1
        )
        if result.returncode == 0:
            return "cuda"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Check for Apple MPS (Metal Performance Shaders)
    if platform.system() == "Darwin":  # macOS
        # Check for Apple Silicon
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                stdout=subprocess.PIPE,
                text=True,
            )
            if "Apple" in result.stdout:
                return "mps"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    # Default to CPU
    print("Neither CUDA nor MPS detected; defaulting to CPU for embeddings.")
    return "cpu"


def detect_host() -> Literal["local", "remote"]:
    """
    Determines host name and whether server should be accessed remote or as localhost.
    """
    hostnames = {
        "remote": ["Botvinnik", "bianders-mn7180.linkedin.biz"],
        "local": ["Caruana"],
    }
    hostname = subprocess.check_output(["hostname"]).decode("utf-8").strip()
    if hostname in hostnames["local"]:
        return "local"
    else:
        return "remote"


async def get_client() -> AsyncClientAPI:
    """
    Get the Chroma client. This is a wrapper around the chromadb.AsyncHttpClient.
    """
    if detect_host() == "local":
        # Localhost
        return await chromadb.AsyncHttpClient(port=8001)
    else:
        # "remote" here means local network (vs. localhost)
        # Can update this later for local vs. remote networks
        return await chromadb.AsyncHttpClient("10.0.0.82", port=8001)


# -----------------------------------------------------------------
# Constants
## Our input data
dir_path = Path(__file__).parent
xlsx_file = dir_path.parent / "data" / "courselist_all.xlsx"
## Configure embedding function
embedding_model: Literal["gtr-t5-large", "all-MiniLM-L6-v2"] = "all-MiniLM-L6-v2"
embedding_function = SentenceTransformerEmbeddingFunction(
    model_name=embedding_model, device=detect_device()
)
## Our chroma client
client = asyncio.run(get_client())  # Preload the client for faster access later
## And this little thing
current = 0  # Global variable for progress bar


def clean_text(text):
    """
    This is useful for all Cosmo data you're bringing in through pandas.
    """
    # Decode HTML entities
    text = html.unescape(text)
    # Handle common encoding issues
    text = text.encode("ascii", "ignore").decode("ascii")
    # Remove any remaining HTML tags
    text = re.sub("<[^<]+?>", "", text)
    return text.strip()


async def heartbeat(client):
    """Generate chroma function; same with the course titles collection."""
    try:
        _ = await client.heartbeat()
        print("Chroma server found.")
    except ValueError as e:
        # Handle tenant/database connection issues
        print(f"Database connection error: {e}")
        raise Exception(f"ChromaDB connection failed - {str(e)}")


async def load_course_titles_from_mongodb():
    """
    Load course titles from MongoDB course_mapping collection into ChromaDB.
    This ensures ChromaDB only contains courses that exist in MongoDB.
    """
    from Kramer.database.MongoDB_course_mapping import get_course_ids, get_course_title

    client = await get_client()
    try:
        await client.delete_collection(name="course_titles")
    except:
        pass

    collection = await client.create_collection(
        name="course_titles", embedding_function=embedding_function
    )

    # Get all course IDs from MongoDB
    course_ids = get_course_ids()
    items = [(course_id, get_course_title(course_id)) for course_id in course_ids]

    # Batch into chunks and load
    chunks = list(enumerate([items[i : i + 500] for i in range(0, len(items), 500)]))
    coroutines = [load_batch(collection, chunk, len(chunks)) for chunk in chunks]
    await asyncio.gather(*coroutines)


async def load_descriptions_from_mongodb():
    """
    Load course descriptions from MongoDB courses collection into ChromaDB.
    Only includes courses that exist in both course_mapping and main courses collection.
    """
    from Kramer.database.MongoDB_CRUD import get_all_courses_sync

    client = await get_client()
    try:
        await client.delete_collection(name="course_descriptions")
    except:
        pass

    collection = await client.create_collection(
        name="course_descriptions", embedding_function=embedding_function
    )

    # Get courses from MongoDB (these are guaranteed to exist)
    courses = get_all_courses_sync()
    items = []
    for course in courses:
        if course.metadata.get("Course Description"):
            items.append(
                (course.course_admin_id, course.metadata["Course Description"])
            )

    # Batch and load
    chunks = list(enumerate([items[i : i + 100] for i in range(0, len(items), 100)]))

    # Progress content manager
    with Progress() as progress:
        task = progress.add_task("[green]Loading ChromaDB...", total=len(chunks))

        async def load_batch_with_progress(collection, chunk) -> None:
            result = await load_batch(collection, chunk, len(chunks))
            progress.advance(task)
            return result

        coroutines = [load_batch_with_progress(collection, chunk) for chunk in chunks]
        await asyncio.gather(*coroutines)


# Batch items into chunks of 100; enumerate them so we can pass the index to the coroutine
async def load_batch(collection: AsyncCollection, chunk: tuple, total: int):
    _, items = chunk
    for item in items:
        await collection.add(
            documents=[item[1]],
            ids=[str(item[0])],
        )


# Query functions
async def query_course_descriptions(query: str, num_results: int = 5) -> list[dict]:
    global client
    collection = await client.get_collection(name="course_descriptions")
    results = await collection.query(query_texts=[query])
    results = list(  # type: ignore
        zip(results["ids"][0][:num_results], results["documents"][0][:num_results])  # type: ignore
    )
    output_list = []
    for result in results:
        course_title = get_course_title(int(result[0]))
        course_description = clean_text(result[1])
        output_list.append(
            {
                "course_title": course_title,
                "course_description": course_description,
            }
        )
    return output_list


def query_course_descriptions_sync(query: str, num_results: int = 5):
    return asyncio.run(query_course_descriptions(query, num_results))


async def main():
    # client = await chromadb.AsyncHttpClient(port=8001)
    # await heartbeat(client)
    # await load_descriptions_into_chroma()
    query = "python essential training algorithms"
    results = await query_course_descriptions(query)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
