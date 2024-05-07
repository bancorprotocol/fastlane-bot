test:
	poetry run pytest fastlane_bot/tests -v $1

pull:
	git pull --recurse-submodules
