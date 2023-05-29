import pytest
import pytest_mock
from pathlib import Path


import numpy as np
from Bio import AlignIO
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment

from clipkit.helpers import count_characters_at_position
from clipkit.helpers import report_column_features
from clipkit.helpers import determine_site_classification_type
from clipkit.helpers import create_keep_and_trim_msas
from clipkit.helpers import write_trim_msa
from clipkit.helpers import write_keep_msa
from clipkit.helpers import SeqType
from clipkit.files import FileFormat

here = Path(__file__)


@pytest.fixture
def sample_msa():
    return MultipleSeqAlignment(
        [
            SeqRecord(
                seq=Seq("['A']"),
                id="1",
                name="<unknown name>",
                description="",
                dbxrefs=[],
            ),
            SeqRecord(
                seq=Seq("['A']"),
                id="2",
                name="<unknown name>",
                description="",
                dbxrefs=[],
            ),
            SeqRecord(
                seq=Seq("['A']"),
                id="3",
                name="<unknown name>",
                description="",
                dbxrefs=[],
            ),
            SeqRecord(
                seq=Seq("['A']"),
                id="4",
                name="<unknown name>",
                description="",
                dbxrefs=[],
            ),
            SeqRecord(
                seq=Seq("['A']"),
                id="5",
                name="<unknown name>",
                description="",
                dbxrefs=[],
            ),
        ]
    )


class TestCountCharactersAtPosition(object):
    def test_gives_count_for_each_char(self):
        ## setup
        s = "ACTTTGGG"

        ## execution
        res = count_characters_at_position(s)

        ## check results
        # test that each character has an associated key
        for char in s:
            assert char in res.keys()

        # test that the len of the res is equal to the
        # number of unique string characters
        assert len(res) == len(set(s))


class TestGetSequenceAtPositionAndReportFeatures(object):
    def test_gets_sequence_and_gappyness(self):
        ## setup
        alignment = AlignIO.read(f"{here.parent}/examples/simple.fa", "fasta")
        i = int(5)

        ## execution
        seq, gappyness = report_column_features(alignment, i, SeqType.nt)

        ## check results
        # test output types
        assert isinstance(seq, str)
        assert isinstance(gappyness, float)


class TestParsimonyInformativeOrConstant(object):
    def test_determine_site_classification_type(self):
        ## set up
        # pi = parsimony informative
        num_occurences_pi = {"A": 5, "T": 10, "G": 2, "C": 4}
        # npi = not parsimony informative
        num_occurences_npi = {"A": 1, "T": 10, "G": 1}
        # Const = constant
        num_occurences_const = {"A": 10}
        # nConst = not constant
        num_occurences_nconst = {"A": 1}

        ## execution
        # result is True and False
        (
            is_parsimony_informative,
            constant_site_holder_is_pi,
        ) = determine_site_classification_type(num_occurences_pi)
        # result is False and False
        (
            is_not_parsimony_informative,
            constant_site_holder_is_npi,
        ) = determine_site_classification_type(num_occurences_npi)
        # result is False and True
        is_not_pi_0, is_constant_site = determine_site_classification_type(
            num_occurences_const
        )
        # result is False and False
        is_not_pi_1, is_not_constant_site = determine_site_classification_type(
            num_occurences_nconst
        )

        ## check results
        assert is_parsimony_informative is True and constant_site_holder_is_pi is False
        assert (
            is_not_parsimony_informative is False
            and constant_site_holder_is_npi is False
        )
        assert is_not_pi_0 is False and is_constant_site is True
        assert is_not_pi_1 is False and is_not_constant_site is False


class TestPopulateEmptyKeepDAndTrimD(object):
    def test_create_keep_and_trim_msas(self):
        ## set up
        alignment = AlignIO.read(f"{here.parent}/examples/simple.fa", "fasta")

        ## execution
        keepD, trimD = create_keep_and_trim_msas(alignment)

        ## check results
        expected_keepD = {
            "1": np.zeros([6], dtype=bytes),
            "2": np.zeros([6], dtype=bytes),
            "3": np.zeros([6], dtype=bytes),
            "4": np.zeros([6], dtype=bytes),
            "5": np.zeros([6], dtype=bytes),
        }
        expected_trimD = {
            "1": np.zeros([6], dtype=bytes),
            "2": np.zeros([6], dtype=bytes),
            "3": np.zeros([6], dtype=bytes),
            "4": np.zeros([6], dtype=bytes),
            "5": np.zeros([6], dtype=bytes),
        }

        assert expected_keepD.keys() == keepD.keys()
        assert all(
            np.array_equal(expected_keepD[key], keepD[key]) for key in expected_keepD
        )
        assert expected_trimD.keys() == trimD.keys()
        assert all(
            np.array_equal(expected_trimD[key], trimD[key]) for key in expected_trimD
        )


class TestWriteKeepD(object):
    def test_write_keep_msa_writes_file(self, mocker, sample_msa):
        ## set up
        keepD = {"1": ["A"], "2": ["A"], "3": ["A"], "4": ["A"], "5": ["A"]}
        out_file = "output_file_name.fa"
        out_file_format = FileFormat.fasta
        mock_msa = mocker.patch("clipkit.helpers.MultipleSeqAlignment")
        mock_msa.return_value = sample_msa
        mock_write = mocker.patch("clipkit.helpers.SeqIO.write")

        ## execution
        write_keep_msa(keepD, out_file, out_file_format)

        ## check results
        mock_write.assert_called_once_with(sample_msa, out_file, out_file_format.value)


class TestWriteTrimD(object):
    def test_write_trim_msa_calls_seqio_write(self, mocker, sample_msa):
        ## set up
        trimD = {"1": ["A"], "2": ["A"], "3": ["A"], "4": ["A"], "5": ["A"]}
        out_file = "output_file_name.fa"
        out_file_format = FileFormat.fasta
        mock_msa = mocker.patch("clipkit.helpers.MultipleSeqAlignment")
        mock_msa.return_value = sample_msa
        mock_write = mocker.patch("Bio.SeqIO.write")

        ## execution
        write_trim_msa(trimD, out_file, out_file_format)

        ## check results
        expected_completmentOut = f"{out_file}.complement"
        mock_write.assert_called_once_with(
            sample_msa, expected_completmentOut, out_file_format.value
        )
