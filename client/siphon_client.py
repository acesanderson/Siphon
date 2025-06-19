from Siphon.data.ContextCall import ContextCall
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.SyntheticData import SyntheticData
import requests, subprocess


class SiphonClient:
    def __init__(self, server_url: str = ""):
        if server_url == "":
            self.server_url = self._get_url()
        else:
            self.server_url = server_url
        self.initialized = False
        self._initialize_client()

    def _initialize_client(self):
        """
        Initialization is a handshake with the server, where we also get our list of ollama_models.
        """
        if not self.server_url:
            self.server_url = self._get_url()
        try:
            response = requests.get(f"{self.server_url}/health")
            response.raise_for_status()
            self.initialized = True
            print("SiphonClient initialized successfully.")
        except requests.RequestException as e:
            raise ConnectionError("Could not connect to Siphon server.")

    def _get_url(self) -> str:
        hostnames = {
            "remote": ["Botvinnik", "bianders-mn7180.linkedin.biz", "Caruana"],
            "local": ["AlphaBlue"],
        }
        # get hostname using subprocess
        hostname = subprocess.check_output(["hostname"]).decode("utf-8").strip()
        if hostname in hostnames["local"]:
            url = "http://localhost:8001"
        else:
            url = "http://10.0.0.87:8001"
        return url

    def request_context_call(self, context_call: ContextCall) -> str:
        """
        Send ContextCall to server for processi tng.
        """
        if not self.initialized:
            raise RuntimeError(
                "SiphonClient is not initialized. Call _initialize_client first."
            )
        response = requests.post(
            f"{self.server_url}/process",
            json=context_call.model_dump(),
            timeout=300,  # 5 min timeout for heavy processing
        )
        response.raise_for_status()
        return str(response.json())

    def request_synthetic_data(
        self, processed_content: ProcessedContent
    ) -> SyntheticData:
        """
        Send ProcessedContent for enrichment.
        """
        if not self.initialized:
            raise RuntimeError(
                "SiphonClient is not initialized. Call _initialize_client first."
            )
        response = requests.post(
            f"{self.server_url}/enrich",
            json=processed_content.model_dump(),
            timeout=300,  # 5 min timeout for heavy processing
        )
        response.raise_for_status()
        synthetic_data = SyntheticData(**response.json())
        return synthetic_data


if __name__ == "__main__":
    # from Siphon.tests.fixtures.example_ProcessedContent import content
    #
    # client = SiphonClient()
    # synthetic_data = client.request_synthetic_data(content)
    # print(synthetic_data)

    from pathlib import Path
    from Siphon.data.ContextCall import create_ContextCall_from_file

    dir_path = Path(__file__).parent
    # file_path = dir_path.parent / "assets" / "duchamp.jpg"
    # image_context_call = create_ContextCall_from_file(file_path)
    # client = SiphonClient()
    # llm_context = client.request_context_call(image_context_call)
    # print(llm_context)

    audio_file_path = dir_path.parent / "assets" / "output.mp3"
    audio_context_call = create_ContextCall_from_file(audio_file_path)
    client = SiphonClient()
    llm_context = client.request_context_call(audio_context_call)
    print(llm_context)
