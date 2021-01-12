"""Tests for the ``omics_ingest.genomics.run_folder`` module."""

from omics_ingest.genomics.illumina.run_folder import (
    NetcopyInfo,
    parse_netcopy_complete_txt,
    runparameters_to_marker_file,
    RunInfo,
    parse_runinfo_xml,
    parse_runparameters_xml,
    RUN_PARAMETERS_AVU_KEY_PREFIX,
)


def test_run_info():
    run_info = RunInfo("flowcell", "instrument", "run_number", "run_id", "date")
    assert list(run_info.to_avus()) == [
        ("omics::ingest::run_info::flowcell", "flowcell", ""),
        ("omics::ingest::run_info::instrument", "instrument", ""),
        ("omics::ingest::run_info::run_number", "run_number", ""),
        ("omics::ingest::run_info::run_id", "run_id", ""),
        ("omics::ingest::run_info::date", "date", ""),
    ]


def test_parse_run_info_a01077():
    """Test for file from NovaSeq A01077."""
    data = parse_runinfo_xml("tests/data/run_folder/RunInfo-A01077.xml")
    assert data.instrument == "A01077"


def test_parse_run_info_k00302():
    """Test for file from HiSeq 4000 K00302."""
    data = parse_runinfo_xml("tests/data/run_folder/RunInfo-K00302.xml")
    assert data.instrument == "K00302"


def test_parse_run_info_m060205():
    """Test for file from MiSeq M06205."""
    data = parse_runinfo_xml("tests/data/run_folder/RunInfo-M06205.xml")
    assert data.instrument == "M06205"


def test_parse_run_info_mn00157():
    """Test for file from MiniSeq MN00157."""
    data = parse_runinfo_xml("tests/data/run_folder/RunInfo-MN00157.xml")
    assert data.instrument == "MN00157"


def test_parse_run_info_nb502131():
    """Test for file from NextSeq NB502131."""
    data = parse_runinfo_xml("tests/data/run_folder/RunInfo-NB502131.xml")
    assert data.instrument == "NB502131"


def test_parse_run_info_st_k00106():
    """Test for file from HiSeq 4000 ST-K00106."""
    data = parse_runinfo_xml("tests/data/run_folder/RunInfo-ST-K00106.xml")
    assert data.instrument == "ST-K00106"


def test_parse_run_parameters_a01077():
    """Test for file from NovaSeq A01077."""
    data = parse_runparameters_xml("tests/data/run_folder/RunParameters-A01077.xml")
    assert data["%s::run_number" % RUN_PARAMETERS_AVU_KEY_PREFIX] == "48"


def test_parse_run_parameters_k00302():
    """Test for file from HiSeq 4000 K00302."""
    data = parse_runparameters_xml("tests/data/run_folder/runParameters-K00302.xml")
    assert data["%s::scan_number" % RUN_PARAMETERS_AVU_KEY_PREFIX] == "168"


def test_parse_run_parameters_m060205():
    """Test for file from MiSeq M06205."""
    data = parse_runparameters_xml("tests/data/run_folder/runParameters-M06205.xml")
    assert data["%s::run_number" % RUN_PARAMETERS_AVU_KEY_PREFIX] == "9"


def test_parse_run_parameters_mn00157():
    """Test for file from MiniSeq MN00157."""
    data = parse_runparameters_xml("tests/data/run_folder/RunParameters-MN00157.xml")
    assert data["%s::run_number" % RUN_PARAMETERS_AVU_KEY_PREFIX] == "67"


def test_parse_run_parameters_nb502131():
    """Test for file from NextSeq NB502131."""
    data = parse_runparameters_xml("tests/data/run_folder/RunParameters-NB502131.xml")
    assert data["%s::run_number" % RUN_PARAMETERS_AVU_KEY_PREFIX] == "93"


def test_parse_run_parameters_st_k00106():
    """Test for file from HiSeq 4000 ST-K00106."""
    data = parse_runparameters_xml("tests/data/run_folder/runParameters-ST-K00106.xml")
    assert data["%s::scan_number" % RUN_PARAMETERS_AVU_KEY_PREFIX] == "95"


def test_netcopy_info():
    ni = NetcopyInfo("6/3/2020", "17:29:14.954", "Illumina RTA 1.18.54")
    assert list(ni.to_avus()) == [
        ("omics::ingest::netcopy_complete::date", "6/3/2020", ""),
        ("omics::ingest::netcopy_complete::time", "17:29:14.954", ""),
        ("omics::ingest::netcopy_complete::rta_version", "Illumina RTA 1.18.54", ""),
    ]


def test_parse_netcopy_complete_txt():
    ni = parse_netcopy_complete_txt(
        "tests/data/run_folder/Basecalling_Netcopy_complete_Read1-M06205.txt"
    )
    assert list(ni.to_avus()) == [
        ("omics::ingest::netcopy_complete::date", "6/3/2020", ""),
        ("omics::ingest::netcopy_complete::time", "17:29:14.954", ""),
        ("omics::ingest::netcopy_complete::rta_version", "Illumina RTA 1.18.54", ""),
    ]


def test_runparameters_to_marker_files_a01077():
    """Test for file from NovaSeq A01077."""
    path = "tests/data/run_folder/RunParameters-A01077.xml"
    data = parse_runparameters_xml(path)
    assert runparameters_to_marker_file(data, path) == ("CopyComplete.txt",)


def test_runparameters_to_marker_files_k00302():
    """Test for file from HiSeq 4000 K00302."""
    path = "tests/data/run_folder/runParameters-K00302.xml"
    data = parse_runparameters_xml(path)
    assert runparameters_to_marker_file(data, path) == ("RTAComplete.txt",)


def test_runparameters_to_marker_files_m060205():
    """Test for file from MiSeq M06205."""
    path = "tests/data/run_folder/runParameters-M06205.xml"
    data = parse_runparameters_xml(path)
    assert runparameters_to_marker_file(data, path) == (
        "Basecalling_Netcopy_complete.txt",
        "ImageAnalysis_Netcopy_complete.txt",
    )


def test_runparameters_to_marker_files_mn00157():
    """Test for file from MiniSeq MN00157."""
    path = "tests/data/run_folder/RunParameters-MN00157.xml"
    data = parse_runparameters_xml(path)
    assert runparameters_to_marker_file(data, path) == ("RTAComplete.txt",)


def test_runparameters_to_marker_files_nb502131():
    """Test for file from NextSeq NB502131."""
    path = "tests/data/run_folder/RunParameters-NB502131.xml"
    data = parse_runparameters_xml(path)
    assert runparameters_to_marker_file(data, path) == ("RTAComplete.txt",)


def test_runparameters_to_marker_files_st_k00106():
    """Test for file from HiSeq 4000 ST-K00106."""
    path = "tests/data/run_folder/runParameters-ST-K00106.xml"
    data = parse_runparameters_xml(path)
    assert runparameters_to_marker_file(data, path) == ("RTAComplete.txt",)
