try:
    from .app import main
except ModuleNotFoundError as exc:
    if exc.name == "tkinter":
        raise SystemExit(
            "This app requires the system tkinter package. On Debian/Ubuntu, install it with: sudo apt install python3-tk"
        ) from exc
    raise


if __name__ == "__main__":
    main()