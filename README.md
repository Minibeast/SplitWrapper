# SplitWrapper
Python wrapper for [LiveSplit](https://livesplit.org) split files.

## Installation
```bash
pip install SplitWrapper
```

## Example Usage
```python
import SplitWrapper
import datetime

# Load the split file

splits = SplitWrapper.load_from_file_path("split.lss")

# Print the Game and Category names

print(splits.GameName, splits.CategoryName)

# Change the attempt count to '63'

splits.AttemptCount = 63

# Create a new segment with a best segment time of 2:44:22 
# and append it to the segments.

new_split = datetime.time(hour=2, minute=44, second=22)
segment = SplitWrapper.Segment()
segment.BestSegmentTime = SplitWrapper.Time(realtime=new_split)
splits.Segments.append(segment)

# Export the splits to a file

SplitWrapper.write_to_file(splits, "newsplits.lss")
```

## Incompatability
The following list details features that are currently not supported:
- Icons of any kind.
- Metadata information.
- Autosplitter settings.
- Split-specific layouts.

There are intentions to add support for these in the future.