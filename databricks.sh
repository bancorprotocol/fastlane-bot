pip install poetry
poetry config virtualenvs.create false
git clone -b release-candidate https://github.com/bancorprotocol/fastlane-bot.git
cd fastlane-bot
poetry install
