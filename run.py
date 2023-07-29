from server import app
from configs.setting import Settings
import uvicorn
import pyfiglet

settings = Settings()

if __name__ == "__main__":
    out = pyfiglet.figlet_format("IDOLBar Client", justify="center", font="slant")
    print(out)
    out = pyfiglet.figlet_format("Ntech", justify="right", font="stop",width=50)
    print(out)
    uvicorn.run(
        "run:app",
        host=settings._host,
        port=settings._port,
        debug=settings._isdebug,
        reload=settings._isreload,
    )
