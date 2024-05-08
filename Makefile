test:
	poetry run pytest fastlane_bot/tests/$(subset)

pull:
	git pull --recurse-submodules
