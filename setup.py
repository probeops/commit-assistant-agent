from setuptools import setup, find_packages

setup(
    name="commit-assistant",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
        "python-dotenv",
        "gitpython",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "commit-assistant=commit_assistant.direct_commit:cli",
        ],
    },
) 