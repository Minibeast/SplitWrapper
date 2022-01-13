from io import TextIOWrapper
import xml.etree.ElementTree as ET
from typing import List
import datetime


class RealTime:
    Value : datetime.time
    
    def __init__(self) -> None:
        self.Value = None
        pass


    def __str__(self) -> str:
        timestring = datetime.time.strftime(self.Value, '%H:%M:%S.%f')
        timestring += "0"
        return timestring


class GameTime:
    Value : datetime.time
    
    def __init__(self) -> None:
        self.Value = None
        pass


    def __str__(self) -> str:
        timestring = datetime.time.strftime(self.Value, '%H:%M:%S.%f')
        timestring += "0"
        return timestring


class Offset:
    Value : datetime.time
    isNegative : bool

    def __init__(self) -> None:
        self.Value = None
        self.isNegative = False
        pass

    def __str__(self) -> str:
        timestring = datetime.time.strftime(self.Value, '%H:%M:%S.%f')
        timestring += "0"
        if self.isNegative:
            timestring = "-" + timestring
        return timestring


class Time:
    RealTime : RealTime
    GameTime : GameTime

    def __init__(self, realtime : datetime.time = None, 
            gametime : datetime.time = None) -> None:
        self.RealTime = RealTime()
        self.GameTime = GameTime()
        
        if realtime is not None:
            self.RealTime.Value = realtime
        if gametime is not None:
            self.GameTime.Value = gametime


    def has_value(self) -> bool:
        return self.RealTime is not None or self.GameTime is not None
    

    def export(self, root : ET.Element) -> None:
        if self.RealTime.Value is not None:
            temp = ET.SubElement(root, "RealTime")
            temp.text = str(self.RealTime)
        if self.GameTime.Value is not None:
            temp = ET.SubElement(root, "GameTime")
            temp.text = str(self.GameTime)


class Attempt:
    id : int
    started : datetime.datetime
    isStartedSynced : bool
    ended : datetime.datetime
    isEndedSynced : bool
    time : Time

    def __init__(self) -> None:
        self.id = None
        self.started = None
        self.isStartedSynced = False
        self.ended = None
        self.isEndedSynced = False
        self.time = Time()
        pass


    def export(self, root : ET.Element) -> None:
        attributes = {
            "id": str(self.id),
            "started": datetime.datetime.strftime(self.started, "%m/%d/%Y %H:%M:%S"),
            "isStartedSynced": str(self.isStartedSynced),
            "ended": datetime.datetime.strftime(self.ended, "%m/%d/%Y %H:%M:%S"),
            "isEndedSynced": str(self.isStartedSynced),
        }
        temp = ET.SubElement(root, "Attempt", attributes)
        if self.time.has_value():
            self.time.export(temp)


class SegmentTimes:
    id : int
    time : Time

    def __init__(self) -> None:
        self.id = None
        self.time = Time()
        pass


    def export(self, root : ET.Element) -> None:
        temp = ET.SubElement(root, "Time", {"id": str(self.id)})
        if self.time.has_value():
            self.time.export(temp)


class SplitTime:
    comparison_name : str
    time : Time

    def __init__(self) -> None:
        self.comparison_name = None
        self.time = Time()
        pass


    def export(self, root : ET.Element) -> None:
        temp = ET.SubElement(root, "SplitTime", {"name": self.comparison_name})
        if self.time.has_value():
            self.time.export(temp)


class Segment:
    name : str
    SplitTimes : List[SplitTime]
    BestSegmentTime : Time
    SegmentHistory : List[SegmentTimes]

    def __init__(self) -> None:
        self.name = None
        self.SplitTimes = []
        self.BestSegmentTime = Time()
        self.SegmentHistory = []
        pass


    def export(self, root : ET.Element) -> None:
        segment = ET.SubElement(root, "Segment")
        name = ET.SubElement(segment, "Name")
        ET.SubElement(segment, "Icon")
        name.text = str(self.name)
        splittimes = ET.SubElement(segment, "SplitTimes")

        for x in self.SplitTimes:
            x.export(splittimes)

        bestsegmenttime = ET.SubElement(segment, "BestSegmentTime")
        if self.BestSegmentTime.has_value():
            self.BestSegmentTime.export(bestsegmenttime)
        
        segmenthistory = ET.SubElement(segment, "SegmentHistory")
        for x in self.SegmentHistory:
            x.export(segmenthistory)


class Splits:
    GameName : str
    CategoryName : str
    Offset : Offset
    AttemptCount : int
    AttemptHistory : List[Attempt]
    Segments : List[Segment]

    def __init__(self) -> None:
        self.GameName = None
        self.CategoryName = None
        self.Offset = Offset()
        self.AttemptCount = None
        self.AttemptHistory = []
        self.Segments = []
        pass


    def parse(self, splits_tree : ET.Element) -> None:
        for x in splits_tree:
            if x.tag == "GameName":
                self.GameName = x.text
            elif x.tag == "CategoryName":
                self.CategoryName = x.text
            elif x.tag == "AttemptCount":
                self.AttemptCount = int(x.text)
            elif x.tag == "Offset":
                self.Offset = parse_offset(x.text)
            elif x.tag == "AttemptHistory":
                self.AttemptHistory = parse_attempthistory(x)
            elif x.tag == "Segments":
                self.Segments = parse_segments(x)
    

    def export(self) -> ET.Element:
        root = ET.Element('Run', attrib={'version': '1.7.0'})
        ET.SubElement(root, "GameIcon")
        gamename = ET.SubElement(root, "GameName")
        gamename.text = str(self.GameName)
        categoryname = ET.SubElement(root, "CategoryName")
        categoryname.text = str(self.CategoryName)
        ET.SubElement(root, "LayoutPath")
        metadata = ET.SubElement(root, "MetaData")
        ET.SubElement(metadata, "Run", {"id": ""})
        ET.SubElement(metadata, "Platform", {"usesEmulator": "False"})
        ET.SubElement(metadata, "Region")
        ET.SubElement(metadata, "Variables")
        offset = ET.SubElement(root, "Offset")
        offset.text = str(self.Offset)
        attemptcount = ET.SubElement(root, "AttemptCount")
        attemptcount.text = str(self.AttemptCount)
        attempthistory = ET.SubElement(root, "AttemptHistory")
        for x in self.AttemptHistory:
            x.export(attempthistory)
        segments = ET.SubElement(root, "Segments")
        for x in self.Segments:
            x.export(segments)
        ET.SubElement(root, "AutoSplitterSettings")
        
        return root
    

    def export_as_string(self) -> str:
        return ET.tostring(self.export(), encoding='unicode', method='xml')


def load_from_file(file : TextIOWrapper) -> Splits:
    root = ET.fromstring(file.read())
    splits = Splits()
    splits.parse(root)
    return splits


def load_from_file_path(path : str) -> Splits:
    tree = ET.parse(path)
    root = tree.getroot()
    splits = Splits()
    splits.parse(root)
    return splits


def load_from_string(text : str) -> Splits:
    root = ET.fromstring(text)
    splits = Splits()
    splits.parse(root)
    return splits


def write_to_file(splits : Splits, path : str) -> None:
    root = splits.export_as_string()
    with open(path, "w+") as file:
        file.write(root)
        file.close()


def parse_offset(offset_tag : str) -> Offset:
    return_offset = Offset()
    if offset_tag[0] == "-":
        return_offset.isNegative = True
    
    return_offset.Value = parse_time(offset_tag)
    return return_offset


def parse_datetime(date : str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%m/%d/%Y %H:%M:%S")


def parse_time(time : str) -> datetime.time:
    time_list = time.split(":")
    microsecond = 0
    if "." in time:
        time_list[len(time_list) - 1] = time_list[len(time_list) - 1].split(".")
        if len(time_list) != 3 or not isinstance(time_list[2], list) or len(time_list[2]) != 2:
            raise KeyError
        microsecond = int(str(time_list[2][1])[:-1])
        second = int(time_list[2][0])
    else:
        second = int(time_list[2])
    if len(time_list) != 3:
        raise KeyError

    return datetime.time(hour=int(time_list[0]), minute=int(time_list[1]),
            second=second, microsecond=microsecond)


def parse_attempthistory(attempts : ET.Element) -> List[Attempt]:
    return_list = []
    for x in attempts:
        attributes = x.attrib
        try:
            attempt = Attempt()
            attempt.id = int(attributes['id'])
            attempt.isStartedSynced = (attributes['isStartedSynced'] == 'True')
            attempt.isEndedSynced = (attributes['isEndedSynced'] == 'True')
            attempt.started = parse_datetime(attributes['started'])
            attempt.ended = parse_datetime(attributes['ended'])
        except:
            raise KeyError
        
        time = Time()
        for y in x:
            if y.tag == "RealTime":
                time.RealTime.Value = parse_time(y.text)
            elif y.tag == "GameTime":
                time.GameTime.Value = parse_time(y.text)
        attempt.time = time

        return_list.append(attempt)

    return return_list


def parse_segments(segments : ET.Element) -> List[Segment]:
    return_list = []
    for segment_itr in segments:
        segment = Segment()
        for x in segment_itr:
            if x.tag == "Name":
                segment.name = x.text
            elif x.tag == "SplitTimes":
                split_times = []
                for y in x:
                    time = Time()
                    splittimes = SplitTime()
                    attributes = y.attrib
                    splittimes.comparison_name = attributes['name']
                    for z in y:
                        if z.tag == "RealTime":
                            time.RealTime.Value = parse_time(z.text)
                        elif z.tag == "GameTime":
                            time.GameTime.Value = parse_time(z.text)
                    splittimes.time = time
                    split_times.append(splittimes)
                segment.SplitTimes = split_times
            elif x.tag == "BestSegmentTime":
                time = Time()
                for y in x:
                    if y.tag == "RealTime":
                        time.RealTime.Value = parse_time(y.text)
                    elif y.tag == "GameTime":
                        time.GameTime.Value = parse_time(y.text)
                segment.BestSegmentTime = time
            elif x.tag == "SegmentHistory":
                segment_history = []
                for y in x:
                    segment_time = SegmentTimes()
                    attributes = y.attrib
                    segment_time.id = attributes['id']
                    time = Time()
                    for z in y:
                        if z.tag == "RealTime":
                            time.RealTime.Value = parse_time(z.text)
                        elif z.tag == "GameTime":
                            time.GameTime.Value = parse_time(z.text)
                    segment_time.time = time
                    segment_history.append(segment_time)
                segment.SegmentHistory = segment_history
        return_list.append(segment)
    return return_list
