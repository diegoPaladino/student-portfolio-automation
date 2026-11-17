Set-Location -LiteralPath $PSScriptRoot
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = 'false'
python -m streamlit run app.py --server.address 127.0.0.1 --server.maxUploadSize 30 --browser.gatherUsageStats false
