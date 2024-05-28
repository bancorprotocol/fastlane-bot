docker_build:
	docker build --tag fastlane-bot --target prod .

docker_run:
	docker run \
		fastlane-bot \
		--arb_mode=b3_two_hop \
		--alchemy_max_block_fetch=20 \
		--loglevel=INFO \
		--backdate_pools=False \
		--polling_interval=0 \
		--reorg_delay=0 \
		--run_data_validator=False \
		--limit_bancor3_flashloan_tokens=True \
		--randomizer=2 \
		--default_min_profit_gas_token=0.001 \
		--exchanges="carbon_v1,bancor_v3,balancer,uniswap_v2_forks,uniswap_v3_forks" \
		--flashloan_tokens="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" \
		--blockchain=ethereum \
		--self_fund=False \
		--read_only=True

docker_test:
	docker build --tag fastlane-bot-tests --target test .
	docker run fastlane-bot-tests

docker_debug:
	docker run \
		-it \
		--entrypoint bash \
		fastlane-bot \
