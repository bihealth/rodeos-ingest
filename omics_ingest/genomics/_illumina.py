"""Helper code for reading Illumina files."""

import typing
import xml.etree.ElementTree as ET

import attr

#: The AVU key prefix to use for run info values.
RUN_INFO_AVU_KEY_PREFIX = "omics::ingest::run_info"


@attr.s(auto_attribs=True, frozen=True)
class RunInfo:
    """Store the information about a run that is extraced from ``RunInfo.xml`` files."""

    #: Flowcell identifier.
    flowcell: str
    #: Instrument identifier.
    instrument: str
    #: Run number.
    run_number: int
    #: Run identifier.
    run_id: str
    #: Date when the flow cell was run.
    date: str

    def to_avus(self):
        """Yield AVU triples for iRODS"""
        for key, value in attr.asdict(self).items():
            yield "{}::{}".format(RUN_INFO_AVU_KEY_PREFIX, key), str(value), ""


def parse_runinfo_xml(path: str) -> RunInfo:
    """Parse information from ``RunInfo.xml`` and return ``RunInfo`` object."""
    tree = ET.parse(path)
    tag_run = tree.find("//Run")
    return RunInfo(
        run_id=tag_run.attrib["Id"],
        run_number=int(tag_run.attrib["Number"]),
        flowcell=tag_run.find("Flowcell").text,
        instrument=tag_run.find("Instrument").text,
        date=tag_run.find("Date").text,
    )


#: The AVU key prefix to use for run parameters values.
RUN_PARAMETERS_AVU_KEY_PREFIX = "omics::ingest::run_parameters"

#: Mapping of XPaths info ``runParameter.xml`` to iRODS AVU names.
RUN_PARAMETERS_XPATH_MAP = {
    ".//FlowcellRFIDTag/SerialNumber": "flowcell_rfid_tag::serial_number",
    ".//FlowcellRFIDTag/PartNumber": "flowcell_rfid_tag::part_number",
    ".//FlowcellRFIDTag/ExpirationDate": "flowcell_rfid_tag::expiration_date",
    ".//PR2BottleRFIDTag/SerialNumber": "pr2_bottle_rfid_tag::serial_number",
    ".//PR2BottleRFIDTag/PartNumber": "pr2_bottle_rfid_tag::part_number",
    ".//PR2BottleRFIDTag/ExpirationDate": "pr2_bottle_rfid_tag::expiration_date",
    ".//ReagentKitRFIDTag/SerialNumber": "reagent_kit_rfid_tag::serial_number",
    ".//ReagentKitRFIDTag/PartNumber": "reagent_kit_rfid_tag::part_number",
    ".//ReagentKitRFIDTag/ExpirationDate": "reagent_kit_rfid_tag::expiration_date",
    ".//RunID": "run_id",
    ".//ScannerID": "scanner_id",
    ".//RunNumber": "run_number",
    ".//FPGAVersion": "fpga_version",
    ".//MCSVersion": "mcs_version",
    ".//RTAVersion": "rta_version",
    ".//Barcode": "barcode",
    ".//PR2BottleBarcode": "pr2_bottle_barcode",
    ".//ReagentKitPartNumberEntered": "reagent_kit_part_number_entered",
    ".//ReagentKitVersion": "reagent_kit_version",
    ".//ReagentKitBarcode": "regaent_kit_barcode",
    ".//SampleSheetName": "sample_sheet_name",
}


def parse_runparameters_xml(path):
    """Parse ``runParameters.xml`` file and return dict of key/value mappings for AVU."""
    tree = ET.parse(path)
    result = {}
    for xpath, key in RUN_PARAMETERS_XPATH_MAP.items():
        elem = tree.find(xpath)
        if elem is not None:
            result["%s::%s" % (RUN_PARAMETERS_AVU_KEY_PREFIX, key)] = elem.text
    return result
