from pydantic import BaseModel
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image


class ImplicitInput(BaseModel):
    """
    Represents an implicit input for our cli.
    This can be content from stdin, clipboard text, or clipboard image.
    Use the `from_environment` class method to create an instance based on the current environment, if you detect there are no args passed to the cli.

    Example:
    ```python
    if len(sys.argv) == 1:
        implicit_input = ImplicitInput.from_environment()
        if implicit_input:
            implicit_input.print() # Prints the content of the implicit input for the user as confirmation.
    ```
    """

    type: Literal["stdin", "clipboard_text", "clipboard_image"]
    content: str | Image

    # Convenience methods
    def print(self) -> None:
        """
        Print the content of the implicit input.
        If it's an image, it will print a placeholder message.
        """
        match self.type:
            case "stdin":
                snippet = str(self.content).strip().replace("\n", " ")[:80]
                print(f"Implicit input from {self.type}: {snippet}...")
            case "clipboard_text":
                snippet = str(self.content).strip().replace("\n", " ")[:80]
                print(f"Implicit input from {self.type}: {snippet}...")
            case "clipboard_image":
                import subprocess, io

                buf = io.BytesIO()
                assert isinstance(self.content, Image), (
                    "Content must be a PIL Image instance"
                )
                self.content.save(buf, format="PNG")
                buf.seek(0)
                # Detect if chafa is available
                try:
                    subprocess.run(
                        ["chafa", "--version"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except FileNotFoundError:
                    print(
                        "chafa is not installed. Please install it to display images in the terminal."
                    )
                    return
                # Print to terminal
                subprocess.run(["chafa", "-"], input=buf.read(), check=True)
            case _:
                raise ValueError(f"Unknown implicit input type: {self.type}")

    # Constructor methods
    @classmethod
    def from_environment(cls) -> "ImplicitInput | None":
        """
        Create an ImplicitInput instance from the environment.
        This contains logic for the naked case, i.e. siphon is called with no arguments. Detects + captures implicit input.
        First detect:
        (1) if stdin was piped (e.g. `cat file.txt | siphon`): capture that and return it.
        (2) detect if clipboard has text: if so, capture that and return it.
        (3) detect if clipboard has an image: if so, capture that and return it.
        (4) if none of the above, return None.
        """
        import sys

        stdin = cls._from_stdin()
        if stdin:
            return stdin
        clipboard_text = cls._from_clipboard_text()
        if clipboard_text:
            return clipboard_text
        clipboard_image = cls._from_clipboard_image()
        if clipboard_image:
            return clipboard_image
        return None

    @classmethod
    def _from_stdin(cls) -> "ImplicitInput | None":
        """
        Create an ImplicitInput instance from stdin.
        """
        import sys

        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                return cls(type="stdin", content=stdin_data.strip())
"
    @classmethod
    def _from_clipboard_text(cls) -> "ImplicitInput | None":
        """
        Create an ImplicitInput instance from clipboard text.
        """
        import pyperclip

        try:
            clip_text = pyperclip.paste()
            if clip_text.strip():
                return cls(type="clipboard_text", content=clip_text.strip())
        except pyperclip.PyperclipException:
            pass

    @classmethod
    def _from_clipboard_image(cls) -> "ImplicitInput | None":
        """
        Create an ImplicitInput instance from clipboard image.
        """
        from PIL import ImageGrab, Image
        import io, subprocess, sys

        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                return cls(
                    type="clipboard_image",
                    content=image,
                )
        except Exception as e:
            print(f"Error processing clipboard image: {e}", file=sys.stderr)

        return None
