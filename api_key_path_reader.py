file_name = "api_key_path_reader.py"
# absolute path to the file holding the api key.
API_KEY_ABS_PATH = __file__.rstrip(file_name) + "api_key"

if __name__ == "__main__":
    print(API_KEY_ABS_PATH)
