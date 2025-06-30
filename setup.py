from setuptools import setup, find_packages

setup(
    name="bsm",
    version="1.0.0",
    description="BullShit Meter - AI-powered fact checker and counter-argument generator",
    author="BSM Development",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "pynput>=1.7.6",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "pyautogui>=0.9.54",
        "keyboard>=0.13.5",
        "pystray>=0.19.4",
        "markdown>=3.5.0",
        "pyyaml>=6.0.1",
        "cryptography>=41.0.0",
        "pytesseract>=0.3.10",
    ],
    entry_points={
        "console_scripts": [
            "bsm=bsm.main:main",
        ],
    },
    python_requires=">=3.8",
)