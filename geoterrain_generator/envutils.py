
import os, pathlib

def load_dotenv(var_name: str, filename=".env"):
    """
    Если в текущем или любом родительском каталоге найден .env и там есть
    строка VAR=VALUE, кладём в os.environ и возвращаем значение.
    """
    here = pathlib.Path(__file__).parent
    for folder in [here, *here.parents]:
        env_path = folder / filename
        if env_path.is_file():
            with env_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip().startswith(f"{var_name}="):
                        _, val = line.split("=", 1)
                        val = val.strip().strip("'\"")
                        os.environ.setdefault(var_name, val)
                        return val
    return None
