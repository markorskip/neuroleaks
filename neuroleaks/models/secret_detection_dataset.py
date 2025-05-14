import random
import json
from datasets import Dataset

random.seed(42)

# === Templates for realistic synthetic secrets ===
SECRET_PATTERNS = [
    lambda: f"aws_access_key_id = \"AKIA{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))}\"",
    lambda: f"aws_secret_access_key = \"{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/+', k=40))}\"",
    lambda: f"token = \"ghp_{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=36))}\"",
    lambda: f"db_password = \"{random.choice(['admin123', 'hunter2', 'passw0rd', '1234abcd'])}\"",
    lambda: f"jwt = \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=30))}.sig\"",
    lambda: f"API_KEY='{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))}'",
    lambda: f"Authorization: Bearer {''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=50))}",
]

# === Templates for realistic non-secret code ===
CLEAN_PATTERNS = [
    "def process_file(path):\n    with open(path) as f:\n        data = f.read()",
    "for i in range(10): print(i)",
    "print('Hello, world!')",
    "def calculate_sum(a, b):\n    return a + b",
    "logger.info('Process started...')",
    "config_path = os.getenv('CONFIG_PATH')",
    "url = 'https://example.com/api/data'",
    "# TODO: implement authentication",
    "password_input = input('Enter password: ')",  # Not hardcoded!
    "token_from_env = os.environ.get('API_TOKEN')",
]

def generate_dataset(n_positive=500, n_negative=500):
    data = []
    for _ in range(n_positive):
        code = random.choice(SECRET_PATTERNS)()
        data.append({"text": code, "label": 1})

    for _ in range(n_negative):
        code = random.choice(CLEAN_PATTERNS)
        data.append({"text": code, "label": 0})

    random.shuffle(data)
    return Dataset.from_list(data)

if __name__ == "__main__":
    dataset = generate_dataset(1000, 1000)
    dataset = dataset.train_test_split(test_size=0.2)
    dataset.save_to_disk("secret_detection_dataset")
    print("✅ Dataset saved to `secret_detection_dataset`")
