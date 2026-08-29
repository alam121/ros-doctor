from setuptools import setup

setup(
    name="robot_driver",
    version="0.1.0",
    packages=["robot_driver"],
    entry_points={
        "console_scripts": [
            "serial_node = robot_driver.serial:main",
        ],
    },
)
