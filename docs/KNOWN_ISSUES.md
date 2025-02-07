# Known Issues and Workarounds for Incredible Squaring AVS (Python) Setup

This document summarizes the known issues and workarounds encountered while setting up the Incredible Squaring AVS in Python, based on a recent debugging session. These notes are intended to help users who may encounter similar problems during the setup process.

**1. CMake Installation Issue**

* **Problem:** Running `cmake ..` resulted in a Python `ModuleNotFoundError` because a Python script named `cmake` was being executed instead of the actual CMake executable.
* **Workaround:** Rename the problematic Python script located at `/home/paul/.local/bin/cmake` to `/home/paul/.local/bin/cmake.python-script`. This allows the system to find and execute the correct CMake executable.

**2. Python Dependency Issues (`pip install -r requirements.txt`)**

* **Initial Problem:** `pip install -r requirements.txt` failed due to a dependency conflict between `web3` versions required by `requirements.txt` and `eigensdk`.
* **Workaround:** Remove the explicit version specification `web3==6.19.0` from `requirements.txt`.
* **Subsequent Problem:** After the initial fix, a `TypeError` related to `ContractEvent.create_filter()` in `eigensdk-python` arose, suggesting incompatibility with a newer `web3` version.
* **Workaround:** Downgrade `web3` to version `6.19.0` *after* installing other requirements using `pip install web3==6.19.0`.
* **Missing Dependency:** `ModuleNotFoundError: No module named 'openai'` occurred when starting the operator.
* **Workaround:** Install the `openai` Python package using `pip install openai` and add `openai` to `requirements.txt`.

**3. `eigensdk-python` Code Fixes (Direct Modifications)**

* **Typo in `raw_transaction` attribute:** `AttributeError` due to incorrect attribute name `raw_transaction` in `eigensdk-python`.
* **Workaround:** Correct the typo in `venv/src/eigensdk/eigensdk/chainio/utils.py`, changing `raw_transaction` to `rawTransaction`.
* **Incorrect method `unsafe_sign_hash`:** `AttributeError` due to the use of non-existent method `account.unsafe_sign_hash` in `eigensdk-python`.
* **Workaround:** Replace `unsafe_sign_hash` with the correct method `account.sign_message(msg_to_sign).signature` in `venv/src/eigensdk/eigensdk/chainio/clients/avsregistry/writer.py`.
* **Indentation Error (`TabError`):** `TabError` in `writer.py` after code modification due to inconsistent use of tabs and spaces.
* **Workaround:** Correct the indentation in `venv/src/eigensdk/eigensdk/chainio/clients/avsregistry/writer.py`, ensuring consistent use of spaces for indentation (convert tabs to spaces).

**4. Configuration Change (`config-files/operator.anvil.yaml`)**

* **Problem:** Operator startup failure with `ContractLogicError: 'execution reverted: DelegationManager.registerAsOperator: operator has already registered'`.
* **Workaround:** Set `register_operator_on_startup: false` in `config-files/operator.anvil.yaml` to disable automatic operator registration on startup.

**5. OpenAI API Related Adjustments**

* **Connection Refused Error:** `httpx.ConnectError` and `openai.APIConnectionError` when operator could not connect to OpenAI server at `http://localhost:6060/v1`.
* **Solution:** Use the official OpenAI API endpoint instead of a local mock server.
* **API Key Issue:** `openai.OpenAIError: The api_key client option must be set...` due to missing `OPENAI_API_KEY` environment variable.
* **Solution:** Set the `OPENAI_API_KEY` environment variable with a valid OpenAI API key.
* **Model Not Found Error:** `openai.NotFoundError` for model `router-mf-0.116` as it's not a standard OpenAI model.
* **Solution:** Change the model name in `routellm.py` to a valid public OpenAI model like `gpt-3.5-turbo`. Also, update the OpenAI API URL in `routellm.py` to `https://api.openai.com/v1`.

**Important Notes:**

* **`eigensdk-python` Patches:** The fixes applied to `eigensdk-python` code are direct modifications within the virtual environment and might be considered temporary workarounds. It is recommended to report these issues to the `eigensdk-python` library maintainers for official fixes.
* **Virtual Environment:** Ensure all `pip install` commands and code modifications are performed within the activated virtual environment to avoid affecting the system Python installation.

This document aims to provide a helpful guide for troubleshooting common issues during the setup of the Incredible Squaring AVS in Python.
