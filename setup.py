from setuptools import setup, find_packages

setup(
    name="Siphon",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "siphon = Siphon.ingestion.siphon:main",
            "record = Siphon.ingestion.audio.record.record:main",
            "play = Siphon.ingestion.audio.record.play:main",
            "siphonserver = Siphon.server.run:main",
            "flatten = Siphon.ingestion.github.flatten_cli:main",
        ],
    },
)
