"""Extract parameter values from PolicyEngine YAML files."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ParameterExtractor:
    """Extract parameter values from YAML parameter files."""

    def __init__(self, repo_path: Path):
        """
        Initialize parameter extractor.

        Args:
            repo_path: Path to policyengine-us repository root
        """
        self.repo_path = repo_path
        self.parameters_path = repo_path / "policyengine_us/parameters"

    def extract_qbi_parameters(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract all QBI-related parameters.

        Args:
            year: Tax year for parameter values (optional)

        Returns:
            Dictionary of parameter paths to values/metadata
        """
        qbi_base = self.parameters_path / "gov/irs/deductions/qbi"

        if not qbi_base.exists():
            raise FileNotFoundError(f"QBI parameters not found at {qbi_base}")

        parameters = {}

        # Process all YAML files
        for yaml_file in qbi_base.rglob("*.yaml"):
            if yaml_file.name == "index.yaml":
                continue

            try:
                param_data = self.extract_parameter_from_file(yaml_file, year)
                if param_data:
                    # Generate parameter path from file location
                    rel_path = yaml_file.relative_to(self.parameters_path)
                    param_path = self._path_to_parameter_name(rel_path)
                    parameters[param_path] = param_data
            except Exception as e:
                print(f"Warning: Failed to parse {yaml_file}: {e}")

        return parameters

    def extract_parameter_from_file(
        self, file_path: Path, year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Extract parameter from a YAML file.

        Args:
            file_path: Path to YAML file
            year: Tax year for parameter value (optional)

        Returns:
            Dictionary with parameter metadata and values
        """
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        if not data:
            return None

        # Get relative path for GitHub link
        rel_path = file_path.relative_to(self.repo_path)

        metadata = {
            "file_path": str(rel_path),
            "description": data.get("description", ""),
            "metadata": data.get("metadata", {}),
            "reference": data.get("reference", []),
            "values": {},
            "current_value": None,
        }

        # Extract values
        if "values" in data:
            metadata["values"] = data["values"]

            # Get current value for specified year
            if year:
                metadata["current_value"] = self._get_value_for_year(
                    data["values"], year
                )

        # Handle different parameter structures
        elif "brackets" in data:
            # Bracket-based parameter (like deduction_floor/amount)
            metadata["type"] = "bracket"
            metadata["brackets"] = data["brackets"]
        elif isinstance(data, dict) and any(
            k for k in data.keys() if k not in ["description", "metadata", "reference"]
        ):
            # May be a direct value or breakdown
            metadata["type"] = "breakdown"
            metadata["breakdown"] = {
                k: v
                for k, v in data.items()
                if k not in ["description", "metadata", "reference"]
            }

        return metadata

    def _get_value_for_year(self, values: dict, year: int) -> Any:
        """
        Get parameter value for a specific year.

        Args:
            values: Dictionary of date/year to values
            year: Tax year

        Returns:
            Parameter value for that year, or most recent if not found
        """
        # Try exact year match
        year_str = str(year)
        if year_str in values:
            return values[year_str]

        # Try YYYY-MM-DD format
        for date_key in sorted(values.keys(), reverse=True):
            if date_key.startswith(year_str):
                return values[date_key]

        # Get most recent value before or equal to year
        valid_dates = []
        for date_key in values.keys():
            try:
                # Extract year from date string
                if "-" in date_key:
                    key_year = int(date_key.split("-")[0])
                else:
                    key_year = int(date_key)

                if key_year <= year:
                    valid_dates.append((key_year, date_key))
            except ValueError:
                continue

        if valid_dates:
            # Return value from most recent valid date
            valid_dates.sort(reverse=True)
            most_recent_key = valid_dates[0][1]
            return values[most_recent_key]

        # Fallback: return first value
        return next(iter(values.values())) if values else None

    @staticmethod
    def _path_to_parameter_name(path: Path) -> str:
        """
        Convert file path to parameter name.

        Example: gov/irs/deductions/qbi/max/rate.yaml
                 -> gov.irs.deductions.qbi.max.rate

        Args:
            path: Path object relative to parameters directory

        Returns:
            Dot-separated parameter name
        """
        # Remove .yaml extension
        parts = list(path.with_suffix("").parts)

        # Join with dots
        return ".".join(parts)
