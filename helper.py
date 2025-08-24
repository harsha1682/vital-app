import os

def load_env_file(filename=".env"):
    env_path = os.path.join(os.getcwd(), filename)
    
    if not os.path.exists(env_path):
        print(f"{filename} not found in {os.getcwd()}")
        return
    
    with open(env_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value
