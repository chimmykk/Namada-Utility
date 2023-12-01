// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.4.0/contracts/token/ERC20/ERC20.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.4.0/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.4.0/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";

contract CustomToken is ERC20, ERC20Burnable, Ownable, ChainlinkClient {
    using Chainlink for Chainlink.Request;

    address public constant DEAD_ADDRESS = 0x000000000000000000000000000000000000dEaD;

    address private oracleAddress;
    bytes32 private jobId;
    uint256 private fee;

    // Here define the Tokenomics 
    uint256 public constant MAX_SUPPLY = 7_000_000_000;
    uint256 public constant INITIAL_SUPPLY = 250_000_000;
    uint256 public constant TEAM_ALLOCATION = 210_000_000;
    uint256 public constant ECOSYSTEM_ALLOCATION = 280_000_000;
    uint256 public constant MINT_FOLLOW = 200;
    uint256 public constant BURN_UNFOLLOW = 100;

    // Team and Ecosystem wallet addresses
    address public constant TEAM_WALLET = 0x3d22B5a58c598bA64276e2B267DD9675f2b45A3E;
    address public constant ECOSYSTEM_WALLET = 0xD5710C51771Dc4F6Ea1d1032b0f623cdA1b63238;

    // Vesting related variables
    uint256 public constant TEAM_VESTING_PERIOD = 1 minutes;
    uint256 public constant TEAM_VESTING_INTERVAL = 1 minutes;
    uint256 public teamLastMintTimestamp;

    event ChainlinkResponseReceived(uint256 value);

    uint256 public prevResponse;
    uint256 public response; // Declare response as a state variable

    constructor() ERC20("CustomToken", "CT") {
        setChainlinkToken(0x6D0F8D488B669aa9BA2D0f0b7B75a88bf5051CD3);
        setOracleAddress(0xa57f0cEd49bB1ed7327f950B12a8419cFD01855f);
        setJobId("a8356f48569c434eaa4ac5fcb4db5cc0");
        setFeeInHundredthsOfLink(1); // 0 LINK

        // Mint initial supply to contract deployer
        _mint(msg.sender, INITIAL_SUPPLY * 10**decimals());

        prevResponse = 0;
        response = 0; // Initialize response
        teamLastMintTimestamp = block.timestamp;
    }

    function requestAndUpdate() external onlyOwner {
        // Request data from Chainlink and set up the Chainlink.Request
        Chainlink.Request memory req = buildOperatorRequest(jobId, this.fulfill.selector);

        req.add("method", "GET");
        req.add("url", "http://35.154.19.254:3000/followercount");
        req.add("headers", '["content-type", "application/json", "set-cookie", "sid=14A52"]');
        req.add("body", "");
        req.add("contact", "derek_linkwellnodes.io");

        req.add("path", "followtech");
        req.addInt("multiplier", 10 * 0);

        // Send the Chainlink request
        sendOperatorRequest(req, fee);

        // Retrieve the response from Chainlink and assign it to localResponse
        uint256 latestResponse = response;

        // Compare previous response with the latest response
        if (prevResponse > latestResponse) {
            // If previous response is higher, burn tokens
            burnAndSendToDeadAddressInternal(BURN_UNFOLLOW);
        } else if (prevResponse < latestResponse) {
            // If previous response is lower, mint tokens
            mintTokenToSupplyInternal(MINT_FOLLOW);
        }
        // Update prevResponse for the next comparison
        prevResponse = latestResponse;
    }

    function mintTokenToSupplyInternal(uint256 amount) internal {
        _mint(owner(), amount * 10**decimals());
    }

    function burnAndSendToDeadAddressInternal(uint256 amountToBurn) internal {
        _burn(msg.sender, amountToBurn * 10**decimals());
        _transfer(msg.sender, DEAD_ADDRESS, amountToBurn * 10**decimals());
    }

    function mintToTeamWallet(uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        require(block.timestamp >= teamLastMintTimestamp + 30 days, "Cannot mint before 1 month");

        // Calculate the maximum amount that can be minted based on the time restriction
        uint256 maxMintableAmount = (TEAM_ALLOCATION / 4);

        // Ensure the new amount does not exceed the ECOSYSTEM_ALLOCATION and the calculated max mintable amount
        require(balanceOf(TEAM_WALLET) + amount <= TEAM_ALLOCATION, "Exceeds ecosystem allocation");
        require(amount <= maxMintableAmount, "Exceeds max mintable amount");

        // Update the teamLastMintTimestamp
        teamLastMintTimestamp = block.timestamp;

        _mint(TEAM_WALLET, amount * (10**decimals()));
    }

    function mintToEcosystemWallet(uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        // Ensure the new amount does not exceed the ECOSYSTEM_ALLOCATION
        require(balanceOf(ECOSYSTEM_WALLET) + amount <= ECOSYSTEM_ALLOCATION, "Exceeds ecosystem allocation");
        _mint(ECOSYSTEM_WALLET, amount * (10**decimals()));
    }

    function mintToSupply(uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        // Ensure the mint amount does not exceed 10 million tokens per transaction
        require(amount <= 10_000_000 * (10**decimals()), "Exceeds max mint per call");
        _mint(owner(), amount * (10**decimals()));
    }

    function setOracleAddress(address _oracleAddress) public onlyOwner {
        oracleAddress = _oracleAddress;
        setChainlinkOracle(_oracleAddress);
    }

    function getOracleAddress() public view onlyOwner returns (address) {
        return oracleAddress;
    }

    function setJobId(string memory _jobId) public onlyOwner {
        jobId = bytes32(bytes(_jobId));
    }

    function getJobId() public view onlyOwner returns (string memory) {
        return string(abi.encodePacked(jobId));
    }

    function setFeeInJuels(uint256 _feeInJuels) public onlyOwner {
        fee = _feeInJuels;
    }

    function setFeeInHundredthsOfLink(uint256 _feeInHundredthsOfLink) public onlyOwner {
        setFeeInJuels((_feeInHundredthsOfLink * LINK_DIVISIBILITY) / 100);
    }

    function getFeeInHundredthsOfLink() public view onlyOwner returns (uint256) {
        return (fee * 100) / LINK_DIVISIBILITY;
    }

    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer LINK tokens"
        );
    }

    function fulfill(bytes32 requestId, uint256 data) public recordChainlinkFulfillment(requestId) {
        // Update the response variable with the received data
        response = data;
        emit ChainlinkResponseReceived(data);
    }
}
