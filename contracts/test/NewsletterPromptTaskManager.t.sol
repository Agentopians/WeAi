// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.12;

import "../src/NewsletterPromptServiceManager.sol" as newsletterPromptServiceManager;
import {NewsletterPromptTaskManager} from "../src/NewsletterPromptTaskManager.sol";
import {BLSMockAVSDeployer} from "@eigenlayer-middleware/test/utils/BLSMockAVSDeployer.sol";
import "../src/INewsletterPromptTaskManager.sol"; // IMPORT INewsletterPromptTaskManager.sol
import {TransparentUpgradeableProxy} from "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";

contract CredibleSquaringTaskManagerTest is BLSMockAVSDeployer {
    newsletterPromptServiceManager.NewsletterPromptServiceManager sm;
    newsletterPromptServiceManager.NewsletterPromptServiceManager smImplementation;
    NewsletterPromptTaskManager tm;
    NewsletterPromptTaskManager tmImplementation;

    uint32 public constant TASK_RESPONSE_WINDOW_BLOCK = 30;
    address aggregator =
        address(uint160(uint256(keccak256(abi.encodePacked("aggregator")))));
    address generator =
        address(uint160(uint256(keccak256(abi.encodePacked("generator")))));

    function setUp() public {
        _setUpBLSMockAVSDeployer();

        tmImplementation = new NewsletterPromptTaskManager(
            registryCoordinator, // Use registryCoordinator directly
            TASK_RESPONSE_WINDOW_BLOCK
        );

        // Third, upgrade the proxy contracts to use the correct implementation contracts and initialize them.
        tm = NewsletterPromptTaskManager(
            address(
                new TransparentUpgradeableProxy(
                    address(tmImplementation),
                    address(proxyAdmin),
                    abi.encodeWithSelector(
                        NewsletterPromptTaskManager.initialize.selector,
                        pauserRegistry,
                        registryCoordinatorOwner,
                        aggregator,
                        generator
                    )
                )
            )
        );
    }

    function testCreateNewTask() public {
        bytes memory quorumNumbers = new bytes(0);
        cheats.prank(generator, generator);
        tm.createNewTask(INewsletterPromptTaskManager.TaskType.VerifyManagerInstructions, "test prompt", 100, quorumNumbers); // Use INewsletterPromptTaskManager.TaskType
        assertEq(tm.latestTaskNum(), 1);
    }
}
