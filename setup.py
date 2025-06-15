from setuptools import setup, find_packages

setup(
    name="Siphon",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "siphon = Siphon.ingestion.siphon:main",
            "record = Siphon.audio.record.record:main",
        ],
    },
)
