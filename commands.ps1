# Define the source and destination paths
$source1 = "C:\Python310\Lib\site-packages\pm4py\objects\bpmn\importer\variants\lxml.py"
$destination1 = "C:\Users\sadeghi\workspace\Phd\Papers\SLURMminer\tool\pm4pyyy\lxml.py"

$source2 = "C:\Python310\Lib\site-packages\pm4py\objects\bpmn\obj.py"
$destination2 = "C:\Users\sadeghi\workspace\Phd\Papers\SLURMminer\tool\pm4pyyy\obj.py"

$destinationDir = "C:\Users\sadeghi\workspace\Phd\Papers\SLURMminer\tool\pm4pyyy\"

# Create the destination directory if it doesn't exist
if (-Not (Test-Path -Path $destinationDir)) {
    New-Item -ItemType Directory -Path $destinationDir
}

# Copy the files to the destination
Copy-Item -Path $source1 -Destination $destination1
Copy-Item -Path $source2 -Destination $destination2
