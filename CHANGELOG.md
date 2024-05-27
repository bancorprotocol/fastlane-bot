# Changelog

## [Unreleased](https://github.com/bancorprotocol/fastlane-bot/tree/HEAD)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v...HEAD)

- last\_updated\_block error when mgr.pool\_data is empty [\#583](https://github.com/bancorprotocol/fastlane-bot/issues/583)

Closed issues

- Bot should only import from top level [\#625](https://github.com/bancorprotocol/fastlane-bot/issues/625)
- Dealing with overlapping strategies in the Optimizer [\#595](https://github.com/bancorprotocol/fastlane-bot/issues/595)
- cvxpy [\#537](https://github.com/bancorprotocol/fastlane-bot/issues/537)

## [v](https://github.com/bancorprotocol/fastlane-bot/tree/v) (2024-05-06)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.9...v)

- \_encoded\_data\[0\] index error [\#584](https://github.com/bancorprotocol/fastlane-bot/issues/584)
- Tests 048, 903 and 906 are broken [\#579](https://github.com/bancorprotocol/fastlane-bot/issues/579)
- The terraformer script is malfunctioning [\#577](https://github.com/bancorprotocol/fastlane-bot/issues/577)
- Key `last_updated_block` not found in dictionary [\#564](https://github.com/bancorprotocol/fastlane-bot/issues/564)
- Erroneous trade instructions possibly not filtered out [\#554](https://github.com/bancorprotocol/fastlane-bot/issues/554)
- Optimzer test fails randomly [\#472](https://github.com/bancorprotocol/fastlane-bot/issues/472)
- Removed fraxswap - not yet supported [\#552](https://github.com/bancorprotocol/fastlane-bot/pull/552) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Solidly V2 stable pools not supported [\#566](https://github.com/bancorprotocol/fastlane-bot/issues/566)
- Fix test 900 [\#562](https://github.com/bancorprotocol/fastlane-bot/issues/562)
- Get rid of checking arb-contract version [\#555](https://github.com/bancorprotocol/fastlane-bot/issues/555)
- Move all one-time initialization outside of the main loop [\#549](https://github.com/bancorprotocol/fastlane-bot/issues/549)

Closed issues

- Main Loop Function / Exception Handling [\#489](https://github.com/bancorprotocol/fastlane-bot/issues/489)

Merged pull requests

- Release candidate [\#619](https://github.com/bancorprotocol/fastlane-bot/pull/619) ([zavelevsky](https://github.com/zavelevsky))
- Add 1 ppm fee to univ3 cal calculator [\#590](https://github.com/bancorprotocol/fastlane-bot/pull/590) ([barakman](https://github.com/barakman))
- NBTest: allowing import from tools without fastlane\_bot [\#589](https://github.com/bancorprotocol/fastlane-bot/pull/589) ([sklbancor](https://github.com/sklbancor))
- OptimizerTesting [\#587](https://github.com/bancorprotocol/fastlane-bot/pull/587) ([sklbancor](https://github.com/sklbancor))
- Fix issue 584 in multicaller.py [\#586](https://github.com/bancorprotocol/fastlane-bot/pull/586) ([barakman](https://github.com/barakman))
- Chore/requirements [\#581](https://github.com/bancorprotocol/fastlane-bot/pull/581) ([platonfloria](https://github.com/platonfloria))
- feat: databricks init script [\#580](https://github.com/bancorprotocol/fastlane-bot/pull/580) ([platonfloria](https://github.com/platonfloria))
- Test900 fails [\#578](https://github.com/bancorprotocol/fastlane-bot/pull/578) ([sklbancor](https://github.com/sklbancor))
- Inject async poa middleware when needed [\#576](https://github.com/bancorprotocol/fastlane-bot/pull/576) ([barakman](https://github.com/barakman))
- Update data files 24 april [\#573](https://github.com/bancorprotocol/fastlane-bot/pull/573) ([barakman](https://github.com/barakman))
- Remove `MultiProviderContractWrapper` [\#571](https://github.com/bancorprotocol/fastlane-bot/pull/571) ([barakman](https://github.com/barakman))
- Remove time-assertions in various tests [\#570](https://github.com/bancorprotocol/fastlane-bot/pull/570) ([barakman](https://github.com/barakman))
- Refrain from including the access-list when it contains an error [\#569](https://github.com/bancorprotocol/fastlane-bot/pull/569) ([barakman](https://github.com/barakman))
- Clean the `manager` module [\#568](https://github.com/bancorprotocol/fastlane-bot/pull/568) ([barakman](https://github.com/barakman))
- Gracefully handle solidly stable pools not supported errors [\#567](https://github.com/bancorprotocol/fastlane-bot/pull/567) ([barakman](https://github.com/barakman))
- Improve error logging when sending private transactions [\#565](https://github.com/bancorprotocol/fastlane-bot/pull/565) ([barakman](https://github.com/barakman))
- Add support for XfaiV0 as a fork of SolidlyV2 [\#563](https://github.com/bancorprotocol/fastlane-bot/pull/563) ([barakman](https://github.com/barakman))
- Module bot cleanup [\#559](https://github.com/bancorprotocol/fastlane-bot/pull/559) ([barakman](https://github.com/barakman))
- Get rid of checking arb-contract version [\#557](https://github.com/bancorprotocol/fastlane-bot/pull/557) ([barakman](https://github.com/barakman))
- Merge rc to dev [\#545](https://github.com/bancorprotocol/fastlane-bot/pull/545) ([zavelevsky](https://github.com/zavelevsky))
- Class TxHelpers Revision \(April 11\) [\#542](https://github.com/bancorprotocol/fastlane-bot/pull/542) ([barakman](https://github.com/barakman))
- chore: poetry project setup [\#534](https://github.com/bancorprotocol/fastlane-bot/pull/534) ([platonfloria](https://github.com/platonfloria))
- Exclude known tax tokens [\#528](https://github.com/bancorprotocol/fastlane-bot/pull/528) ([barakman](https://github.com/barakman))
- Merge main to dev april 08 [\#527](https://github.com/bancorprotocol/fastlane-bot/pull/527) ([barakman](https://github.com/barakman))
- Fixing small stuff [\#513](https://github.com/bancorprotocol/fastlane-bot/pull/513) ([sklbancor](https://github.com/sklbancor))
- Clean the `async_event_update_utils` module [\#511](https://github.com/bancorprotocol/fastlane-bot/pull/511) ([barakman](https://github.com/barakman))
- Clean ABIs following the removal of the factory address retrieval [\#507](https://github.com/bancorprotocol/fastlane-bot/pull/507) ([barakman](https://github.com/barakman))
- Fix json import [\#487](https://github.com/bancorprotocol/fastlane-bot/pull/487) ([barakman](https://github.com/barakman))
- Remove unused module receipt-handler [\#482](https://github.com/bancorprotocol/fastlane-bot/pull/482) ([barakman](https://github.com/barakman))
- Remove the pool-shutdown module, script and test [\#481](https://github.com/bancorprotocol/fastlane-bot/pull/481) ([barakman](https://github.com/barakman))
- Clean the submit-handler and router-handler modules [\#479](https://github.com/bancorprotocol/fastlane-bot/pull/479) ([barakman](https://github.com/barakman))
- Remove unused class `TxHelper` [\#476](https://github.com/bancorprotocol/fastlane-bot/pull/476) ([barakman](https://github.com/barakman))
- Docstrings for files [\#450](https://github.com/bancorprotocol/fastlane-bot/pull/450) ([sklbancor](https://github.com/sklbancor))
- ABI Cleanup [\#435](https://github.com/bancorprotocol/fastlane-bot/pull/435) ([barakman](https://github.com/barakman))
- Solidly curves [\#322](https://github.com/bancorprotocol/fastlane-bot/pull/322) ([sklbancor](https://github.com/sklbancor))

## [v3.1.9](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.9) (2024-04-15)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.8...v3.1.9)

- WEB3\_ALCHEMY\_BASE, WEB3\_FANTOM and WEB3\_MANTLE are missing in the test-suite configuration [\#520](https://github.com/bancorprotocol/fastlane-bot/issues/520)
- Wrong fee resolution used for Solidly forks [\#403](https://github.com/bancorprotocol/fastlane-bot/issues/403)
- Restore exchanges to multichain addresses [\#548](https://github.com/bancorprotocol/fastlane-bot/pull/548) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Update static data mapping files [\#530](https://github.com/bancorprotocol/fastlane-bot/pull/530) ([Lesigh-3100](https://github.com/Lesigh-3100))

Merged pull requests

- Release candidate - Linea support and static data [\#547](https://github.com/bancorprotocol/fastlane-bot/pull/547) ([zavelevsky](https://github.com/zavelevsky))
- Add linea support - hotfix [\#535](https://github.com/bancorprotocol/fastlane-bot/pull/535) ([zavelevsky](https://github.com/zavelevsky))

## [v3.1.8](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.8) (2024-04-13)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.7...v3.1.8)

- Transaction Creation [\#428](https://github.com/bancorprotocol/fastlane-bot/issues/428)

Merged pull requests

- github action support for testing more networks [\#536](https://github.com/bancorprotocol/fastlane-bot/pull/536) ([zavelevsky](https://github.com/zavelevsky))

## [v3.1.7](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.7) (2024-04-11)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.6...v3.1.7)

- supernova not found in exchange [\#539](https://github.com/bancorprotocol/fastlane-bot/issues/539)
- Transactions occasionally revert with error-message `Too little received` [\#383](https://github.com/bancorprotocol/fastlane-bot/issues/383)
- Hotfix - Fix native token address for Mantle [\#541](https://github.com/bancorprotocol/fastlane-bot/pull/541) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Remove unused code in `submithandler.py` [\#350](https://github.com/bancorprotocol/fastlane-bot/issues/350)

Closed issues

- `*args, **kwargs` -\> `argsf1, argsf2`  [\#493](https://github.com/bancorprotocol/fastlane-bot/issues/493)
- Can get rid of the if '-' in cid [\#466](https://github.com/bancorprotocol/fastlane-bot/issues/466)

## [v3.1.6](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.6) (2024-04-10)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.5...v3.1.6)

Merged pull requests

- Update fusionx details info [\#525](https://github.com/bancorprotocol/fastlane-bot/pull/525) ([NIXBNT](https://github.com/NIXBNT))

## [v3.1.5](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.5) (2024-04-09)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.4...v3.1.5)

- Carbon strategies are duplicated from events [\#521](https://github.com/bancorprotocol/fastlane-bot/issues/521)

- Add support for puffs\_penthouse uniswap\_v3 fork [\#524](https://github.com/bancorprotocol/fastlane-bot/pull/524) ([NIXBNT](https://github.com/NIXBNT))

## [v3.1.4](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.4) (2024-04-08)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.3...v3.1.4)

- GPU token external liquidity not found [\#515](https://github.com/bancorprotocol/fastlane-bot/issues/515)
- Hotfix - Carbon strategies duplicated [\#522](https://github.com/bancorprotocol/fastlane-bot/pull/522) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.1.3](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.3) (2024-04-04)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.2...v3.1.3)

- gpu external sources added to event mapping [\#517](https://github.com/bancorprotocol/fastlane-bot/pull/517) ([NIXBNT](https://github.com/NIXBNT))

Closed issues

- All files should have doc strings [\#438](https://github.com/bancorprotocol/fastlane-bot/issues/438)

## [v3.1.2](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.2) (2024-04-01)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.1.1...v3.1.2)

Merged pull requests

- Fix issue 509 [\#510](https://github.com/bancorprotocol/fastlane-bot/pull/510) ([barakman](https://github.com/barakman))

## [v3.1.1](https://github.com/bancorprotocol/fastlane-bot/tree/v3.1.1) (2024-03-27)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.32...v3.1.1)

- Cleopatra and Stratum exchanges not handled correctly [\#488](https://github.com/bancorprotocol/fastlane-bot/issues/488)
- Test files under NBTest [\#448](https://github.com/bancorprotocol/fastlane-bot/issues/448)
- Mantle gas pricing and tx formatting needs to be handled correctly [\#386](https://github.com/bancorprotocol/fastlane-bot/issues/386)
- Incorrect Solidly Factory ABI used for scale & equalizer [\#372](https://github.com/bancorprotocol/fastlane-bot/issues/372)
- Removed Factory address call for Solidly V2 pools [\#495](https://github.com/bancorprotocol/fastlane-bot/pull/495) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Fix for \_get\_layer\_one\_gas\_fee [\#494](https://github.com/bancorprotocol/fastlane-bot/pull/494) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Fix args kwargs usage in build transaction generic [\#492](https://github.com/bancorprotocol/fastlane-bot/pull/492) ([Lesigh-3100](https://github.com/Lesigh-3100))
- RC mantle bugfix for 'last\_updated\_block' key error [\#490](https://github.com/bancorprotocol/fastlane-bot/pull/490) ([mikewcasale](https://github.com/mikewcasale))
- bugfix for get\_tokens\_and\_fee issues [\#485](https://github.com/bancorprotocol/fastlane-bot/pull/485) ([mikewcasale](https://github.com/mikewcasale))
- Restore changes from self funding PR [\#484](https://github.com/bancorprotocol/fastlane-bot/pull/484) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Update static data mantle [\#483](https://github.com/bancorprotocol/fastlane-bot/pull/483) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Change Agni to Pancakeswap fork handling [\#471](https://github.com/bancorprotocol/fastlane-bot/pull/471) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Add missing import to txhelpers [\#452](https://github.com/bancorprotocol/fastlane-bot/pull/452) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Update l1 gas fee logic [\#433](https://github.com/bancorprotocol/fastlane-bot/pull/433) ([mikewcasale](https://github.com/mikewcasale))
- Fix self funding [\#413](https://github.com/bancorprotocol/fastlane-bot/pull/413) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Fix fee resolution for several solidly forks [\#404](https://github.com/bancorprotocol/fastlane-bot/pull/404) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Bugfix custom rpc [\#388](https://github.com/bancorprotocol/fastlane-bot/pull/388) ([mikewcasale](https://github.com/mikewcasale))
- Fix handling of Solidly Factory ABI for equalizer & scale [\#373](https://github.com/bancorprotocol/fastlane-bot/pull/373) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Add Support for multiple Carbon deployments per-chain [\#379](https://github.com/bancorprotocol/fastlane-bot/issues/379)
- Add support for Fantom Network [\#369](https://github.com/bancorprotocol/fastlane-bot/issues/369)
- python main.py --arb\_mode=b3\_two\_hop --alchemy\_max\_block\_fetch=200 --loglevel=INFO --backdate\_pools=False --polling\_interval=0 --reorg\_delay=0 --run\_data\_validator=False --limit\_bancor3\_flashloan\_tokens=True --randomizer=2 --default\_min\_profit\_gas\_token=0.01 --exchanges=carbon\_v1,bancor\_v3,uniswap\_v3,uniswap\_v2,sushiswap\_v2,balancer,pancakeswap\_v2,pancakeswap\_v3 --flashloan\_tokens="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2,0x514910771AF9Ca656af840dff83E8264EcF986CA" [\#367](https://github.com/bancorprotocol/fastlane-bot/issues/367)
- Minor optimization in multicaller [\#348](https://github.com/bancorprotocol/fastlane-bot/issues/348)
- Add Handling of Flashloan Fee [\#346](https://github.com/bancorprotocol/fastlane-bot/issues/346)
- support fusionx v3 on mantle [\#491](https://github.com/bancorprotocol/fastlane-bot/pull/491) ([NIXBNT](https://github.com/NIXBNT))
- 379 support multiple carbon exchanges per chain [\#449](https://github.com/bancorprotocol/fastlane-bot/pull/449) ([mikewcasale](https://github.com/mikewcasale))
- Add Exception to indicate when flashloans are not available on a blockchain [\#417](https://github.com/bancorprotocol/fastlane-bot/pull/417) ([Lesigh-3100](https://github.com/Lesigh-3100))
- 293 reorganize testing infrastructure [\#409](https://github.com/bancorprotocol/fastlane-bot/pull/409) ([mikewcasale](https://github.com/mikewcasale))
- Update mantle static data [\#406](https://github.com/bancorprotocol/fastlane-bot/pull/406) ([Lesigh-3100](https://github.com/Lesigh-3100))
- 381 add ability to split native vs wrapped carbon orders [\#390](https://github.com/bancorprotocol/fastlane-bot/pull/390) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Adds support for Mantle blockchain [\#385](https://github.com/bancorprotocol/fastlane-bot/pull/385) ([NIXBNT](https://github.com/NIXBNT))
- Adds Fantom Support [\#378](https://github.com/bancorprotocol/fastlane-bot/pull/378) ([mikewcasale](https://github.com/mikewcasale))
- 326 fix production job alert spam time outs [\#328](https://github.com/bancorprotocol/fastlane-bot/pull/328) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- Fix rate-limit issue [\#375](https://github.com/bancorprotocol/fastlane-bot/issues/375)

Merged pull requests

- Update release-and-pypi-publish.yml [\#503](https://github.com/bancorprotocol/fastlane-bot/pull/503) ([zavelevsky](https://github.com/zavelevsky))
- touch to trigger release [\#502](https://github.com/bancorprotocol/fastlane-bot/pull/502) ([zavelevsky](https://github.com/zavelevsky))
- touch to trigger release [\#501](https://github.com/bancorprotocol/fastlane-bot/pull/501) ([zavelevsky](https://github.com/zavelevsky))
- touch to trigger auto release [\#500](https://github.com/bancorprotocol/fastlane-bot/pull/500) ([zavelevsky](https://github.com/zavelevsky))
- bumping minor version following mantle support [\#499](https://github.com/bancorprotocol/fastlane-bot/pull/499) ([zavelevsky](https://github.com/zavelevsky))
- Remove the web3 middleware used for mantle interaction [\#496](https://github.com/bancorprotocol/fastlane-bot/pull/496) ([barakman](https://github.com/barakman))
- Release candidate, mantle support and more [\#475](https://github.com/bancorprotocol/fastlane-bot/pull/475) ([zavelevsky](https://github.com/zavelevsky))
- Adds support for Mantle. [\#473](https://github.com/bancorprotocol/fastlane-bot/pull/473) ([mikewcasale](https://github.com/mikewcasale))
- Change default RPC provider for Mantle [\#470](https://github.com/bancorprotocol/fastlane-bot/pull/470) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Add strategy\_id to terraformer [\#451](https://github.com/bancorprotocol/fastlane-bot/pull/451) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Revert "Delete test\_061\_TestWETHConversion.py" [\#444](https://github.com/bancorprotocol/fastlane-bot/pull/444) ([sklbancor](https://github.com/sklbancor))
- Add handling for specific Uni V3 exchanges on Mantle [\#436](https://github.com/bancorprotocol/fastlane-bot/pull/436) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Update NBTest\_070\_TestCarbonTradeSplitter.py [\#434](https://github.com/bancorprotocol/fastlane-bot/pull/434) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Revise the PR for issue 381 [\#431](https://github.com/bancorprotocol/fastlane-bot/pull/431) ([barakman](https://github.com/barakman))
- Declare `async` some of the functions in class `BancorV3` [\#418](https://github.com/bancorprotocol/fastlane-bot/pull/418) ([barakman](https://github.com/barakman))
- Add L1 gas fee calculation [\#414](https://github.com/bancorprotocol/fastlane-bot/pull/414) ([barakman](https://github.com/barakman))
- Minor Cleanup [\#405](https://github.com/bancorprotocol/fastlane-bot/pull/405) ([sklbancor](https://github.com/sklbancor))
- Release candidate - Fantom support [\#391](https://github.com/bancorprotocol/fastlane-bot/pull/391) ([zavelevsky](https://github.com/zavelevsky))
- merge Develop into RC [\#387](https://github.com/bancorprotocol/fastlane-bot/pull/387) ([mikewcasale](https://github.com/mikewcasale))
- Update Base static-pool-data [\#382](https://github.com/bancorprotocol/fastlane-bot/pull/382) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Update main.py [\#380](https://github.com/bancorprotocol/fastlane-bot/pull/380) ([mikewcasale](https://github.com/mikewcasale))
- Ensure that `usd_gastkn_conversion_rate` is always initialized [\#377](https://github.com/bancorprotocol/fastlane-bot/pull/377) ([barakman](https://github.com/barakman))
- Remove unused code [\#368](https://github.com/bancorprotocol/fastlane-bot/pull/368) ([barakman](https://github.com/barakman))
- Simplify and improve event-fetching [\#364](https://github.com/bancorprotocol/fastlane-bot/pull/364) ([barakman](https://github.com/barakman))
- Creating documentation via Sphinx [\#358](https://github.com/bancorprotocol/fastlane-bot/pull/358) ([sklbancor](https://github.com/sklbancor))
- 343 remove test stubs [\#344](https://github.com/bancorprotocol/fastlane-bot/pull/344) ([barakman](https://github.com/barakman))

## [v3.0.32](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.32) (2024-02-09)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.31...v3.0.32)

- Update Base static data & small fix in Terraformer [\#363](https://github.com/bancorprotocol/fastlane-bot/pull/363) ([Lesigh-3100](https://github.com/Lesigh-3100))

Merged pull requests

- Release candidate [\#366](https://github.com/bancorprotocol/fastlane-bot/pull/366) ([zavelevsky](https://github.com/zavelevsky))
- Develop [\#365](https://github.com/bancorprotocol/fastlane-bot/pull/365) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.31](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.31) (2024-02-06)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.30...v3.0.31)

Merged pull requests

- Update static data for Base, fix Sushi V3 Factory address [\#359](https://github.com/bancorprotocol/fastlane-bot/pull/359) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.30](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.30) (2024-02-06)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.29...v3.0.30)

- bug in \_get\_layer\_one\_gas\_fee [\#353](https://github.com/bancorprotocol/fastlane-bot/issues/353)

Merged pull requests

- Revise all submit-transaction methods in the TxHelpers module [\#355](https://github.com/bancorprotocol/fastlane-bot/pull/355) ([barakman](https://github.com/barakman))

## [v3.0.29](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.29) (2024-02-06)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.28...v3.0.29)

- Problems in txhelpers with TX Submission & L1 gas fee calculation [\#351](https://github.com/bancorprotocol/fastlane-bot/issues/351)
- Velocimeter fee calculation not implemented correctly [\#323](https://github.com/bancorprotocol/fastlane-bot/issues/323)
- Update txhelpers.py [\#354](https://github.com/bancorprotocol/fastlane-bot/pull/354) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.28](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.28) (2024-02-04)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.27...v3.0.28)

- Transactions on Base \(and other Optimism forks\) should account for L1 gas fee [\#336](https://github.com/bancorprotocol/fastlane-bot/issues/336)
- Investigate potential Uni V3 data desync [\#296](https://github.com/bancorprotocol/fastlane-bot/issues/296)
- Clean up Solidly fee calculations [\#345](https://github.com/bancorprotocol/fastlane-bot/pull/345) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Add Switch to Utilize Uni V3 Router 02 when necessary [\#285](https://github.com/bancorprotocol/fastlane-bot/issues/285)

## [v3.0.27](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.27) (2024-02-01)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.26...v3.0.27)

- Excessive main loop runtime [\#341](https://github.com/bancorprotocol/fastlane-bot/issues/341)
- Add L1 gas fee calculation on Optimism & forks [\#338](https://github.com/bancorprotocol/fastlane-bot/pull/338) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Add padding to profit vs gas when deciding to execute a transaction [\#329](https://github.com/bancorprotocol/fastlane-bot/issues/329)

## [v3.0.26](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.26) (2024-01-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.25...v3.0.26)

- Failed to get tokens and fee for aerodrome\_v2 [\#337](https://github.com/bancorprotocol/fastlane-bot/issues/337)
- bugfix for excessive main loop runtime [\#342](https://github.com/bancorprotocol/fastlane-bot/pull/342) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.25](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.25) (2024-01-30)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.24...v3.0.25)

- AssertionError for Graphene on Base for strategies that include native ETH [\#330](https://github.com/bancorprotocol/fastlane-bot/issues/330)
- 337 failed to get tokens and fee for aerodrome v2 [\#339](https://github.com/bancorprotocol/fastlane-bot/pull/339) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.24](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.24) (2024-01-30)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.23...v3.0.24)

- Trading on aerodrome\_v2 is not properly supported [\#331](https://github.com/bancorprotocol/fastlane-bot/issues/331)
- Add function native\_gas\_token\_to\_wrapped and remove Ethereum only forconversion in routehandler.py \_calc\_carbon\_output [\#332](https://github.com/bancorprotocol/fastlane-bot/pull/332) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.23](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.23) (2024-01-29)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.22...v3.0.23)

- Block number can be float when fetching events leading to failure [\#301](https://github.com/bancorprotocol/fastlane-bot/issues/301)
- 331 trading on aerodrome v2 is not properly supported [\#333](https://github.com/bancorprotocol/fastlane-bot/pull/333) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.22](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.22) (2024-01-24)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.21...v3.0.22)

- hex string without 0x prefix [\#306](https://github.com/bancorprotocol/fastlane-bot/issues/306)

Merged pull requests

- Fix the calculation of a non-integer block number [\#320](https://github.com/bancorprotocol/fastlane-bot/pull/320) ([barakman](https://github.com/barakman))

## [v3.0.21](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.21) (2024-01-23)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.20...v3.0.21)

- max priority fee overridden in build\_transaction\_with\_gas when gas base fee fails [\#300](https://github.com/bancorprotocol/fastlane-bot/issues/300)
- hex string without 0x prefix [\#324](https://github.com/bancorprotocol/fastlane-bot/pull/324) ([mikewcasale](https://github.com/mikewcasale))

- Add support for Solidly Uni V2-style pools [\#274](https://github.com/bancorprotocol/fastlane-bot/issues/274)

Closed issues

- Fix production job alert spam \(time-outs\) [\#325](https://github.com/bancorprotocol/fastlane-bot/issues/325)

## [v3.0.20](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.20) (2024-01-22)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.19...v3.0.20)

- 274 add support for solidly uni v2 style pools [\#282](https://github.com/bancorprotocol/fastlane-bot/pull/282) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.19](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.19) (2024-01-22)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.18...v3.0.19)

- Production monitoring spreadsheet [\#275](https://github.com/bancorprotocol/fastlane-bot/issues/275)

Merged pull requests

- Log the entire stack-trace upon main-loop exceptions [\#318](https://github.com/bancorprotocol/fastlane-bot/pull/318) ([barakman](https://github.com/barakman))
- Log all non-integer block numbers in function `get_start_block` [\#316](https://github.com/bancorprotocol/fastlane-bot/pull/316) ([barakman](https://github.com/barakman))
- Improve the handling of the error-message returned from the node [\#304](https://github.com/bancorprotocol/fastlane-bot/pull/304) ([barakman](https://github.com/barakman))

## [v3.0.18](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.18) (2024-01-18)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.17...v3.0.18)

Merged pull requests

- Solidly Analytics [\#315](https://github.com/bancorprotocol/fastlane-bot/pull/315) ([sklbancor](https://github.com/sklbancor))

## [v3.0.17](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.17) (2024-01-17)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.16...v3.0.17)

Merged pull requests

- Return `None` when the 2nd call to `construct_contract_function` fails [\#312](https://github.com/bancorprotocol/fastlane-bot/pull/312) ([barakman](https://github.com/barakman))

## [v3.0.16](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.16) (2024-01-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.15...v3.0.16)

- Max priority fee input overridden when handling incorrect base fee input error [\#307](https://github.com/bancorprotocol/fastlane-bot/issues/307)

Merged pull requests

- Log the type and value of each variable passed to function `get_start_block` [\#303](https://github.com/bancorprotocol/fastlane-bot/pull/303) ([barakman](https://github.com/barakman))

## [v3.0.15](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.15) (2024-01-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.14...v3.0.15)

- Bancor V2 ETH pool has wrong Anchor address [\#309](https://github.com/bancorprotocol/fastlane-bot/issues/309)

Merged pull requests

- Fix max\_priority usage in txhelpers & pool\_shutdown [\#308](https://github.com/bancorprotocol/fastlane-bot/pull/308) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.14](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.14) (2024-01-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.13...v3.0.14)

- Update static\_pool\_data.csv [\#310](https://github.com/bancorprotocol/fastlane-bot/pull/310) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.13](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.13) (2024-01-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.12...v3.0.13)

- Add eval back due to bug [\#305](https://github.com/bancorprotocol/fastlane-bot/pull/305) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.12](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.12) (2024-01-14)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.11...v3.0.12)

- Update uniswap\_v3\_event\_mappings.csv [\#298](https://github.com/bancorprotocol/fastlane-bot/pull/298) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.11](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.11) (2024-01-14)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.10...v3.0.11)

- Hex string without 0x prefix [\#287](https://github.com/bancorprotocol/fastlane-bot/issues/287)
- Bugfixes for production environment [\#297](https://github.com/bancorprotocol/fastlane-bot/pull/297) ([mikewcasale](https://github.com/mikewcasale))

- Add read-only setting [\#288](https://github.com/bancorprotocol/fastlane-bot/issues/288)

## [v3.0.10](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.10) (2024-01-11)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.9...v3.0.10)

- Add Test Coverage: Arb Modes [\#281](https://github.com/bancorprotocol/fastlane-bot/issues/281)
- 288 add read only setting [\#290](https://github.com/bancorprotocol/fastlane-bot/pull/290) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.9](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.9) (2024-01-08)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.8...v3.0.9)

- Incorrect fee for sushiswap v2 ethereum in multichain\_addresses.csv [\#283](https://github.com/bancorprotocol/fastlane-bot/issues/283)

- 281 add test coverage arb modes [\#286](https://github.com/bancorprotocol/fastlane-bot/pull/286) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.8](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.8) (2024-01-05)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.7...v3.0.8)

- 283 incorrect fee for sushiswap v2 ethereum in multichain addressescsv [\#284](https://github.com/bancorprotocol/fastlane-bot/pull/284) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.7](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.7) (2024-01-01)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.6...v3.0.7)

Merged pull requests

- Create FAQ.md [\#273](https://github.com/bancorprotocol/fastlane-bot/pull/273) ([zavelevsky](https://github.com/zavelevsky))

## [v3.0.6](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.6) (2023-12-28)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.5...v3.0.6)

Merged pull requests

- update default click params [\#278](https://github.com/bancorprotocol/fastlane-bot/pull/278) ([mikewcasale](https://github.com/mikewcasale))

## [v3.0.5](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.5) (2023-12-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.4...v3.0.5)

- minor spelling issue txhelpers \(coinbase\_bse\) [\#269](https://github.com/bancorprotocol/fastlane-bot/issues/269)

Merged pull requests

- Create pull\_request\_template.md [\#272](https://github.com/bancorprotocol/fastlane-bot/pull/272) ([zavelevsky](https://github.com/zavelevsky))
- Update issue templates [\#271](https://github.com/bancorprotocol/fastlane-bot/pull/271) ([zavelevsky](https://github.com/zavelevsky))

## [v3.0.4](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.4) (2023-12-22)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.3...v3.0.4)

- Bug in POL Mode & Carbon Curve creation [\#266](https://github.com/bancorprotocol/fastlane-bot/issues/266)
- Update txhelpers.py [\#270](https://github.com/bancorprotocol/fastlane-bot/pull/270) ([NIXBNT](https://github.com/NIXBNT))

## [v3.0.3](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.3) (2023-12-21)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.2...v3.0.3)

- Minor bugs in Bot V3 [\#264](https://github.com/bancorprotocol/fastlane-bot/issues/264)
- Remove token key in POL mode & add try/except for Carbon curve creation [\#267](https://github.com/bancorprotocol/fastlane-bot/pull/267) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v3.0.2](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.2) (2023-12-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v3.0.1...v3.0.2)

- Fixes to Multichain addresses & static data for Base, Polygon, and Arbitrum [\#265](https://github.com/bancorprotocol/fastlane-bot/pull/265) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Add support for trades without Flashloans [\#200](https://github.com/bancorprotocol/fastlane-bot/issues/200)

## [v3.0.1](https://github.com/bancorprotocol/fastlane-bot/tree/v3.0.1) (2023-12-19)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.83...v3.0.1)

- Fix error caused in poolandtokens for Bancor POL curves [\#254](https://github.com/bancorprotocol/fastlane-bot/issues/254)
- bugfix for missing pool data [\#178](https://github.com/bancorprotocol/fastlane-bot/issues/178)
- Bug in utils.py update\_pools\_from\_contracts [\#125](https://github.com/bancorprotocol/fastlane-bot/issues/125)
- Incorrect address field for bancor\_v3 in static\_pool\_data.csv [\#118](https://github.com/bancorprotocol/fastlane-bot/issues/118)

- Remove disabled pools from Bancor V3 static data [\#151](https://github.com/bancorprotocol/fastlane-bot/issues/151)
- Change tx submit directly to flashbots \(instead of Alchemy\) [\#106](https://github.com/bancorprotocol/fastlane-bot/issues/106)
- Add Target Token Mode for Recent Events [\#98](https://github.com/bancorprotocol/fastlane-bot/issues/98)
- Add Support for Curve Exchange [\#75](https://github.com/bancorprotocol/fastlane-bot/issues/75)
- Generalize `b3_two_hop` to allow handling arbs between external exchanges only. [\#73](https://github.com/bancorprotocol/fastlane-bot/issues/73)
- Consolidate DEFAULT\_MIN\_PROFIT\_BNT and DEFAULT\_MIN\_PROFIT variables [\#59](https://github.com/bancorprotocol/fastlane-bot/issues/59)
- Add Support for Bancor V3 Vortex Trigger [\#44](https://github.com/bancorprotocol/fastlane-bot/issues/44)
- Refactor Code to Prevent Silent Failure of Exceptions [\#39](https://github.com/bancorprotocol/fastlane-bot/issues/39)
- Bot 3.0 [\#262](https://github.com/bancorprotocol/fastlane-bot/pull/262) ([Lesigh-3100](https://github.com/Lesigh-3100))

Closed issues

- Error writing pool data to disk: Object of type int64 is not JSON serializable [\#259](https://github.com/bancorprotocol/fastlane-bot/issues/259)
- main.py / env [\#104](https://github.com/bancorprotocol/fastlane-bot/issues/104)
- Version number via CLI [\#23](https://github.com/bancorprotocol/fastlane-bot/issues/23)
- Transaction is stuck in mempool [\#5](https://github.com/bancorprotocol/fastlane-bot/issues/5)

## [v2.7.83](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.83) (2023-12-12)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.82...v2.7.83)

- Issue causing transactions to be submitted without Flashbots by default [\#251](https://github.com/bancorprotocol/fastlane-bot/issues/251)
- update LYXe token info [\#241](https://github.com/bancorprotocol/fastlane-bot/issues/241)
- Bancor POL fix for poolandtokens [\#255](https://github.com/bancorprotocol/fastlane-bot/pull/255) ([Lesigh-3100](https://github.com/Lesigh-3100))

Merged pull requests

- Update tokens.csv [\#242](https://github.com/bancorprotocol/fastlane-bot/pull/242) ([NIXBNT](https://github.com/NIXBNT))

## [v2.7.82](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.82) (2023-12-12)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.81...v2.7.82)

- Issue with Bancor POL Balance updating after trades [\#249](https://github.com/bancorprotocol/fastlane-bot/issues/249)
- Update txhelpers.py [\#252](https://github.com/bancorprotocol/fastlane-bot/pull/252) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.81](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.81) (2023-12-11)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.80...v2.7.81)

Merged pull requests

- 249 issue with bancor pol balance updating after trades [\#250](https://github.com/bancorprotocol/fastlane-bot/pull/250) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.80](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.80) (2023-12-11)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.79...v2.7.80)

- bugfix pstart [\#248](https://github.com/bancorprotocol/fastlane-bot/pull/248) ([NIXBNT](https://github.com/NIXBNT))

- Improve logging error messages [\#243](https://github.com/bancorprotocol/fastlane-bot/issues/243)

## [v2.7.79](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.79) (2023-12-10)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.78...v2.7.79)

- Update Fast Lane contract address on Base [\#244](https://github.com/bancorprotocol/fastlane-bot/issues/244)
- 243 improve logging error messages [\#247](https://github.com/bancorprotocol/fastlane-bot/pull/247) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- Can anyone provide the instructions to use a private eth node? Already have the node [\#246](https://github.com/bancorprotocol/fastlane-bot/issues/246)

## [v2.7.78](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.78) (2023-12-07)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.77...v2.7.78)

- default\_min\_profit\_gas\_token too low by default [\#239](https://github.com/bancorprotocol/fastlane-bot/issues/239)
- Update network.py [\#245](https://github.com/bancorprotocol/fastlane-bot/pull/245) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.77](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.77) (2023-11-29)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.76...v2.7.77)

- Add logic for ETH/WETH wrapping & unwrapping [\#214](https://github.com/bancorprotocol/fastlane-bot/issues/214)
- Arb Bot Upgrade for next POL iteration [\#194](https://github.com/bancorprotocol/fastlane-bot/issues/194)
- Add triangle arb mode for Bancor POL pools [\#157](https://github.com/bancorprotocol/fastlane-bot/issues/157)
- Further process all arb opportunities [\#100](https://github.com/bancorprotocol/fastlane-bot/issues/100)

Merged pull requests

- update the default min profit [\#240](https://github.com/bancorprotocol/fastlane-bot/pull/240) ([NIXBNT](https://github.com/NIXBNT))

## [v2.7.76](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.76) (2023-11-29)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.75...v2.7.76)

- Error reading updating pool decimals [\#235](https://github.com/bancorprotocol/fastlane-bot/issues/235)

- Major Update - handles upcoming changes to the Fast Lane smart contract [\#237](https://github.com/bancorprotocol/fastlane-bot/pull/237) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.75](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.75) (2023-11-29)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.74...v2.7.75)

- add float wrapper incase decimal input is string [\#236](https://github.com/bancorprotocol/fastlane-bot/pull/236) ([NIXBNT](https://github.com/NIXBNT))

Closed issues

- Update Arb Mode descriptions in Readme [\#233](https://github.com/bancorprotocol/fastlane-bot/issues/233)

## [v2.7.74](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.74) (2023-11-28)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.73...v2.7.74)

- Target token bug [\#225](https://github.com/bancorprotocol/fastlane-bot/issues/225)

Merged pull requests

- Update README.md [\#234](https://github.com/bancorprotocol/fastlane-bot/pull/234) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.73](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.73) (2023-11-28)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.72...v2.7.73)

- Specific exchanges bug [\#226](https://github.com/bancorprotocol/fastlane-bot/issues/226)
- If gas tkn or wrapped gas token is in flashloan tokens, always include both in token list [\#232](https://github.com/bancorprotocol/fastlane-bot/pull/232) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Add handling for instances where Stablecoin pool cannot be found for … [\#231](https://github.com/bancorprotocol/fastlane-bot/pull/231) ([Lesigh-3100](https://github.com/Lesigh-3100))

Closed issues

- USDC missing from tokens.csv [\#229](https://github.com/bancorprotocol/fastlane-bot/issues/229)

## [v2.7.72](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.72) (2023-11-27)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.71...v2.7.72)

- Add missing pool data [\#227](https://github.com/bancorprotocol/fastlane-bot/issues/227)

Merged pull requests

- Update tokens.csv [\#230](https://github.com/bancorprotocol/fastlane-bot/pull/230) ([NIXBNT](https://github.com/NIXBNT))

## [v2.7.71](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.71) (2023-11-26)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.70...v2.7.71)

- Access List handling in TxHelpers should have its own try/except [\#223](https://github.com/bancorprotocol/fastlane-bot/issues/223)

Merged pull requests

- Update uniswap\_v3\_event\_mappings.csv [\#228](https://github.com/bancorprotocol/fastlane-bot/pull/228) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.70](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.70) (2023-11-23)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.69...v2.7.70)

- Minor bug fix in Carbon calculations [\#222](https://github.com/bancorprotocol/fastlane-bot/issues/222)
- "strategy" error in multi mode [\#220](https://github.com/bancorprotocol/fastlane-bot/issues/220)
- Add standalone try except for Access List and improve error logging [\#224](https://github.com/bancorprotocol/fastlane-bot/pull/224) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.69](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.69) (2023-11-21)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.68...v2.7.69)

- Precision Update 2 [\#206](https://github.com/bancorprotocol/fastlane-bot/issues/206)
- bugfix strategy error [\#221](https://github.com/bancorprotocol/fastlane-bot/pull/221) ([NIXBNT](https://github.com/NIXBNT))

- Remove dependencies on profit calculations [\#173](https://github.com/bancorprotocol/fastlane-bot/issues/173)

## [v2.7.68](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.68) (2023-11-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.67...v2.7.68)

- Scan logging for unknown errors failing silently [\#217](https://github.com/bancorprotocol/fastlane-bot/issues/217)

- 206 precision update 2 [\#219](https://github.com/bancorprotocol/fastlane-bot/pull/219) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.67](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.67) (2023-11-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.66...v2.7.67)

- Handle token decimals of None type [\#215](https://github.com/bancorprotocol/fastlane-bot/issues/215)
- Create scan\_log\_errors.py [\#218](https://github.com/bancorprotocol/fastlane-bot/pull/218) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.66](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.66) (2023-11-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.65...v2.7.66)

- adds handling for decimals of None type [\#216](https://github.com/bancorprotocol/fastlane-bot/pull/216) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- multiple runtime errors in latest main branch [\#213](https://github.com/bancorprotocol/fastlane-bot/issues/213)
- fix current version requirements.txt file [\#207](https://github.com/bancorprotocol/fastlane-bot/issues/207)

## [v2.7.65](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.65) (2023-11-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.64...v2.7.65)

- Bugfix in flashloan generation [\#210](https://github.com/bancorprotocol/fastlane-bot/issues/210)

Merged pull requests

- added version checker and requirements change [\#208](https://github.com/bancorprotocol/fastlane-bot/pull/208) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.64](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.64) (2023-11-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.63...v2.7.64)

- Add prefix option to file paths which are written \(for deployment job write permissions\) [\#204](https://github.com/bancorprotocol/fastlane-bot/issues/204)
- Convert tkn key when WETH \> ETH for single-flashloan creation [\#211](https://github.com/bancorprotocol/fastlane-bot/pull/211) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.63](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.63) (2023-11-15)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.62...v2.7.63)

- Add support for Graphene on Base [\#198](https://github.com/bancorprotocol/fastlane-bot/issues/198)
- 204 add prefix option to file paths which are written for deployment job write permissions [\#205](https://github.com/bancorprotocol/fastlane-bot/pull/205) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.62](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.62) (2023-11-15)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.61...v2.7.62)

- Bug - ensure no precision or rounding error when generating trades through Carbon [\#201](https://github.com/bancorprotocol/fastlane-bot/issues/201)

- Add addresses & handling to route through Graphene on Base [\#199](https://github.com/bancorprotocol/fastlane-bot/pull/199) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.61](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.61) (2023-11-14)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.60...v2.7.61)

- Fix to use wei format for generating flashloans to avoid precision or rounding errors [\#202](https://github.com/bancorprotocol/fastlane-bot/pull/202) ([Lesigh-3100](https://github.com/Lesigh-3100))

Closed issues

- Warning! Error encountered during contract execution \[execution reverted\]  [\#195](https://github.com/bancorprotocol/fastlane-bot/issues/195)
- Ensure backward compatibility for python 3.8 in light of new async changes [\#188](https://github.com/bancorprotocol/fastlane-bot/issues/188)

## [v2.7.60](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.60) (2023-11-13)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.59...v2.7.60)

- Bug in automatic pool shutdown [\#192](https://github.com/bancorprotocol/fastlane-bot/issues/192)

Merged pull requests

- removing incompatible type reference for upcoming web3.py version change [\#189](https://github.com/bancorprotocol/fastlane-bot/pull/189) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.59](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.59) (2023-11-13)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.58...v2.7.59)

- Bugfix in auto pool shutdown [\#193](https://github.com/bancorprotocol/fastlane-bot/pull/193) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Tokens with shutdown pools should be flashloaned from Balancer [\#196](https://github.com/bancorprotocol/fastlane-bot/issues/196)

## [v2.7.58](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.58) (2023-11-13)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.57...v2.7.58)

- Wrong router address for Uni V3 [\#190](https://github.com/bancorprotocol/fastlane-bot/issues/190)

- 196 tokens with shutdown pools should be flashloaned from balancer [\#197](https://github.com/bancorprotocol/fastlane-bot/pull/197) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.57](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.57) (2023-11-10)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.56...v2.7.57)

- Fix router address for Uni V3 [\#191](https://github.com/bancorprotocol/fastlane-bot/pull/191) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.56](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.56) (2023-11-09)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.55...v2.7.56)

- Add multichain support [\#183](https://github.com/bancorprotocol/fastlane-bot/pull/183) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.55](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.55) (2023-11-01)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.54...v2.7.55)

- Bug in close pool script [\#181](https://github.com/bancorprotocol/fastlane-bot/issues/181)

Merged pull requests

- Revert "adds base\_path to the get\_static\_data fn" [\#185](https://github.com/bancorprotocol/fastlane-bot/pull/185) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.54](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.54) (2023-10-30)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.53...v2.7.54)

- zero liquidity pool filters Carbon Orders where y0 is 0 but y1 isn't [\#176](https://github.com/bancorprotocol/fastlane-bot/issues/176)
- adds base\_path to the get\_static\_data fn [\#182](https://github.com/bancorprotocol/fastlane-bot/pull/182) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.53](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.53) (2023-10-28)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.52...v2.7.53)

- Add the ability to get all pools [\#174](https://github.com/bancorprotocol/fastlane-bot/issues/174)

Closed issues

- unsupported operand type\(s\) for -: 'float' and 'decimal.Decimal' [\#180](https://github.com/bancorprotocol/fastlane-bot/issues/180)

Merged pull requests

- Fix a bug that filtered Carbon Strategies with an empty order 0 [\#177](https://github.com/bancorprotocol/fastlane-bot/pull/177) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.52](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.52) (2023-10-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.51...v2.7.52)

- Several bugs - static pool csv and validator [\#171](https://github.com/bancorprotocol/fastlane-bot/issues/171)

- Create terraformer [\#175](https://github.com/bancorprotocol/fastlane-bot/pull/175) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.51](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.51) (2023-10-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.50...v2.7.51)

- Bancor V2 Events Filtering Issue [\#168](https://github.com/bancorprotocol/fastlane-bot/issues/168)
- Fix bug in validate\_optimizer\_trades and readd Balancer pools to stat… [\#172](https://github.com/bancorprotocol/fastlane-bot/pull/172) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.50](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.50) (2023-10-13)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.49...v2.7.50)

- goalseek should use eps as a ratio [\#138](https://github.com/bancorprotocol/fastlane-bot/issues/138)
- Update event filtering to remove Bancor V2 anchors [\#169](https://github.com/bancorprotocol/fastlane-bot/pull/169) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.49](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.49) (2023-10-12)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.48...v2.7.49)

- modified the goalseek to use eps as a ratio [\#139](https://github.com/bancorprotocol/fastlane-bot/pull/139) ([NIXBNT](https://github.com/NIXBNT))

- Add Support for Pancakeswap \(on Ethereum\) Exchange [\#81](https://github.com/bancorprotocol/fastlane-bot/issues/81)

## [v2.7.48](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.48) (2023-10-12)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.47...v2.7.48)

- Rate limiter for free alchemy accounts [\#166](https://github.com/bancorprotocol/fastlane-bot/issues/166)
- 81 add support for pancakeswap on ethereum exchange [\#156](https://github.com/bancorprotocol/fastlane-bot/pull/156) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.47](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.47) (2023-10-12)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.46...v2.7.47)

- bug when identifying wrong-direction Carbon curves in Balancer multi pair mode [\#164](https://github.com/bancorprotocol/fastlane-bot/issues/164)

- adds rate limiter and removes unnecessary alchemy calls for chain\_id [\#167](https://github.com/bancorprotocol/fastlane-bot/pull/167) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.46](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.46) (2023-10-09)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.45...v2.7.46)

- Update pairwise\_multi\_bal.py [\#165](https://github.com/bancorprotocol/fastlane-bot/pull/165) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Add Support for Balancer Exchange [\#70](https://github.com/bancorprotocol/fastlane-bot/issues/70)

## [v2.7.45](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.45) (2023-10-05)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.44...v2.7.45)

- Update Bancor Network ABI [\#162](https://github.com/bancorprotocol/fastlane-bot/issues/162)

- Add balancer [\#160](https://github.com/bancorprotocol/fastlane-bot/pull/160) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.44](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.44) (2023-10-05)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.43...v2.7.44)

Merged pull requests

- Update Bancor Network ABI [\#163](https://github.com/bancorprotocol/fastlane-bot/pull/163) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.43](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.43) (2023-10-03)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.42...v2.7.43)

- Bug with new multicall method when running backdate\_pools=True [\#158](https://github.com/bancorprotocol/fastlane-bot/issues/158)
- Update run\_pool\_shutdown.py [\#161](https://github.com/bancorprotocol/fastlane-bot/pull/161) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.42](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.42) (2023-10-01)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.41...v2.7.42)

- Fix or replace brownie multicall functionality [\#137](https://github.com/bancorprotocol/fastlane-bot/issues/137)
- 158 bug with new multicall method when running backdate pools=true [\#159](https://github.com/bancorprotocol/fastlane-bot/pull/159) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.41](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.41) (2023-09-29)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.40...v2.7.41)

- Remove Tenderly default for Bancor POL in contracts.py get\_pool\_contract [\#153](https://github.com/bancorprotocol/fastlane-bot/issues/153)

- 137 fix or replace brownie multicall functionality [\#155](https://github.com/bancorprotocol/fastlane-bot/pull/155) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.40](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.40) (2023-09-26)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.39...v2.7.40)

- Fix block start number for POL contract [\#149](https://github.com/bancorprotocol/fastlane-bot/issues/149)
- Remove Tenderly Web3 instantiation [\#154](https://github.com/bancorprotocol/fastlane-bot/pull/154) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.39](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.39) (2023-09-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.38...v2.7.39)

- Update BANCOR\_POL\_START\_BLOCK to correct value [\#150](https://github.com/bancorprotocol/fastlane-bot/pull/150) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Add support for POL Contract [\#109](https://github.com/bancorprotocol/fastlane-bot/issues/109)

## [v2.7.38](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.38) (2023-09-22)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.37...v2.7.38)

- pol merge bug on mainnet [\#147](https://github.com/bancorprotocol/fastlane-bot/issues/147)

Merged pull requests

- Optimizer tests [\#146](https://github.com/bancorprotocol/fastlane-bot/pull/146) ([sklbancor](https://github.com/sklbancor))

## [v2.7.37](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.37) (2023-09-21)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.36...v2.7.37)

- bugfix for POL on mainnet [\#148](https://github.com/bancorprotocol/fastlane-bot/pull/148) ([mikewcasale](https://github.com/mikewcasale))

- Checklist for Adding Tests to Bancor POL Contract Support [\#116](https://github.com/bancorprotocol/fastlane-bot/issues/116)

## [v2.7.36](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.36) (2023-09-21)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.35...v2.7.36)

- 109 pol and tenderly cleanup [\#136](https://github.com/bancorprotocol/fastlane-bot/pull/136) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- need a more comprehensive list of univ2 event mappings [\#140](https://github.com/bancorprotocol/fastlane-bot/issues/140)

## [v2.7.35](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.35) (2023-09-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.34...v2.7.35)

- bancor v2 pool key bug [\#142](https://github.com/bancorprotocol/fastlane-bot/issues/142)

Merged pull requests

- Update uniswap\_v2\_event\_mappings.csv [\#141](https://github.com/bancorprotocol/fastlane-bot/pull/141) ([NIXBNT](https://github.com/NIXBNT))

## [v2.7.34](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.34) (2023-09-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.33...v2.7.34)

- Fix manager tests [\#144](https://github.com/bancorprotocol/fastlane-bot/issues/144)
- bugfix for b2 key value [\#143](https://github.com/bancorprotocol/fastlane-bot/pull/143) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.33](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.33) (2023-09-20)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.32...v2.7.33)

- Update event\_test\_data.json [\#145](https://github.com/bancorprotocol/fastlane-bot/pull/145) ([mikewcasale](https://github.com/mikewcasale))

- Implement new PairOptimizer for pairwise arbitrage modes [\#134](https://github.com/bancorprotocol/fastlane-bot/issues/134)

## [v2.7.32](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.32) (2023-09-18)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.31...v2.7.32)

- Bug that causes invalid TX [\#132](https://github.com/bancorprotocol/fastlane-bot/issues/132)

- Add support for tenderly testing without replay mode [\#112](https://github.com/bancorprotocol/fastlane-bot/issues/112)
- change optimizer class and method for pairwise modes [\#135](https://github.com/bancorprotocol/fastlane-bot/pull/135) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.31](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.31) (2023-09-18)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.30...v2.7.31)

Merged pull requests

- Patch to handle removal of 0-input trades [\#133](https://github.com/bancorprotocol/fastlane-bot/pull/133) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.30](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.30) (2023-09-18)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.29...v2.7.30)

Closed issues

- Error in main loop: \[\<class 'decimal.DivisionUndefined'\>\] [\#130](https://github.com/bancorprotocol/fastlane-bot/issues/130)

Merged pull requests

- Optimization [\#124](https://github.com/bancorprotocol/fastlane-bot/pull/124) ([sklbancor](https://github.com/sklbancor))

## [v2.7.29](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.29) (2023-09-17)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.28...v2.7.29)

- Fixed a division by zero bug. [\#131](https://github.com/bancorprotocol/fastlane-bot/pull/131) ([mikewcasale](https://github.com/mikewcasale))

- Change tests to use python 3.8 [\#128](https://github.com/bancorprotocol/fastlane-bot/issues/128)

## [v2.7.28](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.28) (2023-09-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.27...v2.7.28)

- Remove python 3.8 incompatible type-hints [\#126](https://github.com/bancorprotocol/fastlane-bot/issues/126)

- Update tests to run python 3.8 [\#129](https://github.com/bancorprotocol/fastlane-bot/pull/129) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.27](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.27) (2023-09-16)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.26...v2.7.27)

- Bugfix for python 3.8 type-hints [\#127](https://github.com/bancorprotocol/fastlane-bot/pull/127) ([mikewcasale](https://github.com/mikewcasale))

- Always submit max amountIn for last trade per-tkn [\#121](https://github.com/bancorprotocol/fastlane-bot/issues/121)

## [v2.7.26](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.26) (2023-09-14)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.25...v2.7.26)

- Add support for automatic pool shutdown [\#115](https://github.com/bancorprotocol/fastlane-bot/issues/115)
- Add a function that changes sourceAmount to 0 for the last trade per TKN [\#122](https://github.com/bancorprotocol/fastlane-bot/pull/122) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.25](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.25) (2023-09-14)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.24...v2.7.25)

- Bug where a deleted carbon strategy event breaks the main.py loop. [\#114](https://github.com/bancorprotocol/fastlane-bot/issues/114)

- 115 add support for automatic pool shutdown [\#123](https://github.com/bancorprotocol/fastlane-bot/pull/123) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.24](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.24) (2023-09-12)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.23...v2.7.24)

- Bancor V2 bug when exchange not included, or address not found [\#110](https://github.com/bancorprotocol/fastlane-bot/issues/110)
- Fix for strategy deleted event [\#120](https://github.com/bancorprotocol/fastlane-bot/pull/120) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Implement Replay Mode to Recreate Historical Ethereum Scenarios Using Tenderly Forks [\#61](https://github.com/bancorprotocol/fastlane-bot/issues/61)

## [v2.7.23](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.23) (2023-09-08)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.22...v2.7.23)

- Deleted strategy breaks Carbon initial multicall [\#107](https://github.com/bancorprotocol/fastlane-bot/issues/107)
- 110 bancor v2 bug when exchange not included or address not found [\#111](https://github.com/bancorprotocol/fastlane-bot/pull/111) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.22](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.22) (2023-09-06)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.21...v2.7.22)

- move strategy deleted event to be with other Carbon events [\#108](https://github.com/bancorprotocol/fastlane-bot/pull/108) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Change default settings to `--backdate_pools=True` for `bancor_v2` support [\#103](https://github.com/bancorprotocol/fastlane-bot/issues/103)
- Add support for Balancer flashloans. [\#77](https://github.com/bancorprotocol/fastlane-bot/issues/77)

## [v2.7.21](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.21) (2023-09-04)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.20...v2.7.21)

- Balancer Flashloans now supported & used automatically when needed [\#97](https://github.com/bancorprotocol/fastlane-bot/pull/97) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.20](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.20) (2023-09-03)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.19...v2.7.20)

- block number fix in bot.py \_get\_deadline function [\#105](https://github.com/bancorprotocol/fastlane-bot/pull/105) ([Lesigh-3100](https://github.com/Lesigh-3100))

- Various Optimizations [\#99](https://github.com/bancorprotocol/fastlane-bot/issues/99)
- Add Non-Overwriting Logging for Successful Transactions [\#36](https://github.com/bancorprotocol/fastlane-bot/issues/36)

## [v2.7.19](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.19) (2023-08-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.18...v2.7.19)

- Adds advanced logging infrastructure for multiple bot instance loggin… [\#95](https://github.com/bancorprotocol/fastlane-bot/pull/95) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.18](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.18) (2023-08-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.17...v2.7.18)

-  list index out of range \[main loop\] [\#101](https://github.com/bancorprotocol/fastlane-bot/issues/101)

Merged pull requests

- Balancer2 [\#88](https://github.com/bancorprotocol/fastlane-bot/pull/88) ([sklbancor](https://github.com/sklbancor))

## [v2.7.17](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.17) (2023-08-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.16...v2.7.17)

Merged pull requests

- fixes a bug from replay mode that impacts when running non-replay modes [\#102](https://github.com/bancorprotocol/fastlane-bot/pull/102) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.16](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.16) (2023-08-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.15...v2.7.16)

- 61 implement replay mode [\#96](https://github.com/bancorprotocol/fastlane-bot/pull/96) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- More verbose info on startup [\#26](https://github.com/bancorprotocol/fastlane-bot/issues/26)

## [v2.7.15](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.15) (2023-08-30)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.14...v2.7.15)

- Jupytext does not exist for automated tests [\#89](https://github.com/bancorprotocol/fastlane-bot/issues/89)

- Adds complete runtime configuration to startup logs. Adds logging to … [\#94](https://github.com/bancorprotocol/fastlane-bot/pull/94) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.14](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.14) (2023-08-30)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.13...v2.7.14)

- Add jupytext dependency for automated test script [\#93](https://github.com/bancorprotocol/fastlane-bot/pull/93) ([mikewcasale](https://github.com/mikewcasale))

- Add Support for Trader Joe Exchange [\#71](https://github.com/bancorprotocol/fastlane-bot/issues/71)
- Add Support for Bancor V2 Exchange [\#69](https://github.com/bancorprotocol/fastlane-bot/issues/69)

## [v2.7.13](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.13) (2023-08-28)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.12...v2.7.13)

- Broken tests [\#92](https://github.com/bancorprotocol/fastlane-bot/issues/92)
- test\_902\_ValidatorSlow non-recurrent \(?\) issue [\#25](https://github.com/bancorprotocol/fastlane-bot/issues/25)

- Add flashloan token liquidity check. [\#80](https://github.com/bancorprotocol/fastlane-bot/issues/80)
- Improve Repo History Lineage Lost During Codebase Overwrite from v1.0 to v2.0 [\#34](https://github.com/bancorprotocol/fastlane-bot/issues/34)
- 69 add support for bancor v2 exchange [\#91](https://github.com/bancorprotocol/fastlane-bot/pull/91) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.12](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.12) (2023-08-28)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.11...v2.7.12)

- fix issue in which validator test could randomly fail [\#90](https://github.com/bancorprotocol/fastlane-bot/pull/90) ([Lesigh-3100](https://github.com/Lesigh-3100))

## [v2.7.11](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.11) (2023-08-27)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.10...v2.7.11)

- Cleanup `main.py` for improved logical clarity of steps. [\#85](https://github.com/bancorprotocol/fastlane-bot/issues/85)
- Balancer base code, part 1 [\#87](https://github.com/bancorprotocol/fastlane-bot/pull/87) ([sklbancor](https://github.com/sklbancor))

## [v2.7.10](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.10) (2023-08-21)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.9...v2.7.10)

- Bugfix: Remove DAI from `flashloan_tokens` [\#78](https://github.com/bancorprotocol/fastlane-bot/issues/78)

- Add support for new Carbon contract custom fees per strategy [\#41](https://github.com/bancorprotocol/fastlane-bot/issues/41)
- 85 cleanup mainpy for improved logical clarity of steps [\#86](https://github.com/bancorprotocol/fastlane-bot/pull/86) ([mikewcasale](https://github.com/mikewcasale))
- Adds support for custom fee contract changes [\#84](https://github.com/bancorprotocol/fastlane-bot/pull/84) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.9](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.9) (2023-08-13)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.8...v2.7.9)

- Remove DAI from default `flashloan_tokens` to fix logging error message. [\#79](https://github.com/bancorprotocol/fastlane-bot/pull/79) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- Broken Link To Github [\#64](https://github.com/bancorprotocol/fastlane-bot/issues/64)

## [v2.7.8](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.8) (2023-08-10)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.7...v2.7.8)

- Fix broken pypi automation [\#66](https://github.com/bancorprotocol/fastlane-bot/issues/66)

Merged pull requests

- Fix Github Link [\#65](https://github.com/bancorprotocol/fastlane-bot/pull/65) ([shmuel44](https://github.com/shmuel44))

## [v2.7.7](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.7) (2023-08-10)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.6...v2.7.7)

- Update release-and-pypi-publish.yml [\#67](https://github.com/bancorprotocol/fastlane-bot/pull/67) ([mikewcasale](https://github.com/mikewcasale))

- Feature Request: Add `target_tokens` Setting to Narrow Search Space [\#62](https://github.com/bancorprotocol/fastlane-bot/issues/62)

## [v2.7.6](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.6) (2023-08-09)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.5...v2.7.6)

- Change the `--flashloan_tokens` flag type to list [\#57](https://github.com/bancorprotocol/fastlane-bot/issues/57)

- 62 add target tokens setting to narrow search space [\#63](https://github.com/bancorprotocol/fastlane-bot/pull/63) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.5](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.5) (2023-08-09)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.4...v2.7.5)

- Fix to ensure the @click flag for flashloan\_tokens is respected [\#58](https://github.com/bancorprotocol/fastlane-bot/pull/58) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- Installation Issue with pyyaml==5.4.1 and Brownie [\#30](https://github.com/bancorprotocol/fastlane-bot/issues/30)

## [v2.7.4](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.4) (2023-08-07)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.3...v2.7.4)

- Cleanup of Unused Top-Level Files [\#47](https://github.com/bancorprotocol/fastlane-bot/issues/47)

Merged pull requests

- Creates a bash install script to handle the conda vs pip installation… [\#51](https://github.com/bancorprotocol/fastlane-bot/pull/51) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.3](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.3) (2023-08-07)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.2...v2.7.3)

- Removes unused files. [\#48](https://github.com/bancorprotocol/fastlane-bot/pull/48) ([mikewcasale](https://github.com/mikewcasale))

Closed issues

- Update README with Brownie and pyyaml Install Troubleshoot [\#31](https://github.com/bancorprotocol/fastlane-bot/issues/31)

## [v2.7.2](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.2) (2023-08-07)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.1...v2.7.2)

- Change automation to increment patch version instead of minor version. [\#53](https://github.com/bancorprotocol/fastlane-bot/issues/53)

Merged pull requests

- Adds additional installation instructions for apple-silicon users. [\#52](https://github.com/bancorprotocol/fastlane-bot/pull/52) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.1](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.1) (2023-08-06)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.7.0...v2.7.1)

- Change automation to increment patch version instead of minor. [\#54](https://github.com/bancorprotocol/fastlane-bot/pull/54) ([mikewcasale](https://github.com/mikewcasale))

## [v2.7.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.7.0) (2023-08-02)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.6.0...v2.7.0)

- Add new GitHub action for automating production job restart upon new version update. [\#46](https://github.com/bancorprotocol/fastlane-bot/issues/46)
- Adding to exiting workflow instead of stand-alone [\#50](https://github.com/bancorprotocol/fastlane-bot/pull/50) ([mikewcasale](https://github.com/mikewcasale))

## [v2.6.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.6.0) (2023-07-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.5.0...v2.6.0)

- b3\_two\_hop Arb Mode Resulting in Losses Due to Lack of Data Validation [\#42](https://github.com/bancorprotocol/fastlane-bot/issues/42)
- Increase DEFAULT\_MIN\_PROFIT\_BNT Value & Fix Hardcoding Issue in config/network.py [\#37](https://github.com/bancorprotocol/fastlane-bot/issues/37)
- Bug: Overwriting of flashloan\_tokens List Set in main.py [\#35](https://github.com/bancorprotocol/fastlane-bot/issues/35)

- 46 add new GitHub action for automating production job restart upon new version update [\#49](https://github.com/bancorprotocol/fastlane-bot/pull/49) ([mikewcasale](https://github.com/mikewcasale))

## [v2.5.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.5.0) (2023-07-31)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.4.0...v2.5.0)

- Unassigned 'rate\_limiter' Error with Shared Alchemy API Key [\#32](https://github.com/bancorprotocol/fastlane-bot/issues/32)
- Adds data validation to `b3_two_hop` mode by default. [\#43](https://github.com/bancorprotocol/fastlane-bot/pull/43) ([mikewcasale](https://github.com/mikewcasale))

## [v2.4.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.4.0) (2023-07-27)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.3.0...v2.4.0)

- bugfix closes \#32 [\#33](https://github.com/bancorprotocol/fastlane-bot/pull/33) ([mikewcasale](https://github.com/mikewcasale))

## [v2.3.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.3.0) (2023-07-26)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.2.0...v2.3.0)

Merged pull requests

- Merging DEVSKL from the old repo into the new repo [\#17](https://github.com/bancorprotocol/fastlane-bot/pull/17) ([sklbancor](https://github.com/sklbancor))

## [v2.2.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.2.0) (2023-07-26)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725g...v2.2.0)

Merged pull requests

- Bugfix/automated release action [\#29](https://github.com/bancorprotocol/fastlane-bot/pull/29) ([mikewcasale](https://github.com/mikewcasale))
- Bugfix/GitHub actions [\#28](https://github.com/bancorprotocol/fastlane-bot/pull/28) ([mikewcasale](https://github.com/mikewcasale))
- Bump version \[skip ci\] [\#21](https://github.com/bancorprotocol/fastlane-bot/pull/21) ([bancor-services](https://github.com/bancor-services))
- Bump version \[skip ci\] [\#20](https://github.com/bancorprotocol/fastlane-bot/pull/20) ([bancor-services](https://github.com/bancor-services))
- updating DEFAULT\_MIN\_PROFIT\_BNT to 1 [\#19](https://github.com/bancorprotocol/fastlane-bot/pull/19) ([mikewcasale](https://github.com/mikewcasale))

## [main_skl_flbot_20230725g](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725g) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725f...main_skl_flbot_20230725g)

## [main_skl_flbot_20230725f](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725f) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725e...main_skl_flbot_20230725f)

## [main_skl_flbot_20230725e](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725e) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725d...main_skl_flbot_20230725e)

## [main_skl_flbot_20230725d](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725d) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725c...main_skl_flbot_20230725d)

## [main_skl_flbot_20230725c](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725c) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725b...main_skl_flbot_20230725c)

## [main_skl_flbot_20230725b](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725b) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/main_skl_flbot_20230725...main_skl_flbot_20230725b)

## [main_skl_flbot_20230725](https://github.com/bancorprotocol/fastlane-bot/tree/main_skl_flbot_20230725) (2023-07-25)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v2.1.0...main_skl_flbot_20230725)

## [v2.1.0](https://github.com/bancorprotocol/fastlane-bot/tree/v2.1.0) (2023-07-24)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/v1.0...v2.1.0)

Merged pull requests

- Bump version \[skip ci\] [\#15](https://github.com/bancorprotocol/fastlane-bot/pull/15) ([bancor-services](https://github.com/bancor-services))
- Bump version \[skip ci\] [\#14](https://github.com/bancorprotocol/fastlane-bot/pull/14) ([bancor-services](https://github.com/bancor-services))

## [v1.0](https://github.com/bancorprotocol/fastlane-bot/tree/v1.0) (2023-05-23)

[Full Changelog](https://github.com/bancorprotocol/fastlane-bot/compare/8ba1c6eebf13a8ff8e550cb28ea86e7e286e4e43...v1.0)

Merged pull requests

- Feature/read reward settings from arb contract [\#10](https://github.com/bancorprotocol/fastlane-bot/pull/10) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Fix typo in readme [\#9](https://github.com/bancorprotocol/fastlane-bot/pull/9) ([Lesigh-3100](https://github.com/Lesigh-3100))
- update arb function name [\#8](https://github.com/bancorprotocol/fastlane-bot/pull/8) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Update contract ABI [\#7](https://github.com/bancorprotocol/fastlane-bot/pull/7) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Feature/contract upgrade [\#6](https://github.com/bancorprotocol/fastlane-bot/pull/6) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Feature/private transactions [\#4](https://github.com/bancorprotocol/fastlane-bot/pull/4) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Bugfix/collection path [\#3](https://github.com/bancorprotocol/fastlane-bot/pull/3) ([Lesigh-3100](https://github.com/Lesigh-3100))
- Dev [\#2](https://github.com/bancorprotocol/fastlane-bot/pull/2) ([mikewcasale](https://github.com/mikewcasale))
- Dev [\#1](https://github.com/bancorprotocol/fastlane-bot/pull/1) ([mikewcasale](https://github.com/mikewcasale))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
