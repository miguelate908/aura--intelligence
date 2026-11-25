"""Configuration shared by backend tests."""
import os

# Use a dedicated 64-byte key before importing modules that read it at startup.
os.environ["JWT_SECRET_KEY"] = "public-test-key-" * 4
