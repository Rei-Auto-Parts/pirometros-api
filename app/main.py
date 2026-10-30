import sys

from infra.init.ioc_init import build_api_entry


def main() -> int:
    build_api_entry().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
