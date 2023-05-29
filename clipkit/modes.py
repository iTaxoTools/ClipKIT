from enum import Enum
from typing import TYPE_CHECKING
from .logger import log_file_logger

if TYPE_CHECKING:
    from .helpers import SiteClassificationType
    from Bio.Align import MultipleSeqAlignment
    from .msa import MSA


class TrimmingMode(Enum):
    gappy = "gappy"
    smart_gap = "smart-gap"
    kpi = "kpi"
    kpi_gappy = "kpi-gappy"
    kpi_smart_gap = "kpi-smart-gap"
    kpic = "kpic"
    kpic_gappy = "kpic-gappy"
    kpic_smart_gap = "kpic-smart-gap"


def should_keep_site(
    mode: TrimmingMode,
    site_classification_type: "SiteClassificationType",
    gappyness: float,
    gaps: float,
) -> bool:
    if mode == TrimmingMode.kpi_gappy:
        return gappyness <= gaps and site_classification_type.parsimony_informative
    elif mode == TrimmingMode.gappy:
        return gappyness <= gaps
    elif mode == TrimmingMode.kpi:
        return site_classification_type.parsimony_informative
    elif mode == TrimmingMode.kpic:
        return (
            site_classification_type.parsimony_informative
            or site_classification_type.constant_site
        )
    elif mode == TrimmingMode.kpic_gappy:
        return gappyness <= gaps and (
            site_classification_type.parsimony_informative
            or site_classification_type.constant_site
        )
    elif mode == TrimmingMode.smart_gap:
        return round(gappyness, 4) < gaps
    elif mode == TrimmingMode.kpic_smart_gap:
        return round(gappyness, 4) < gaps and (
            site_classification_type.parsimony_informative
            or site_classification_type.constant_site
        )
    elif mode == TrimmingMode.kpi_smart_gap:
        return (
            round(gappyness, 4) < gaps
            and site_classification_type.parsimony_informative
        )


def trim(
    gappyness: float,
    site_classification_type: "SiteClassificationType",
    site_classification_counts: dict,
    keep_msa: dict,
    trim_msa: dict,
    alignment_position: int,
    gaps: float,
    alignment: "MultipleSeqAlignment",
    mode: TrimmingMode,
    use_log: bool,
) -> tuple["MSA", "MSA"]:
    if should_keep_site(mode, site_classification_type, gappyness, gaps):
        site_classification_counts[site_classification_type] += 1
        for entry in alignment:
            new_value = entry.seq._data[alignment_position : alignment_position + 1]
            keep_msa.set_entry_sequence_at_position(
                entry.description, alignment_position, new_value
            )
        if use_log:
            log_file_logger.debug(
                f"{str(alignment_position + 1)} keep {site_classification_type.value} {gappyness}"
            )
    elif trim_msa is not None:
        for entry in alignment:
            new_value = entry.seq._data[alignment_position : alignment_position + 1]
            trim_msa.set_entry_sequence_at_position(
                entry.description, alignment_position, new_value
            )
        if use_log:
            log_file_logger.debug(
                f"{str(alignment_position + 1)} trim {site_classification_type.value} {gappyness}"
            )

    return keep_msa, trim_msa
