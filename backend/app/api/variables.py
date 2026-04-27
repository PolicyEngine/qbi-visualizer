"""API endpoints for variables."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional

from app.config import settings
from app.models.variable import VariableMetadata, VariableList, VariableGraph
from app.services.github_manager import GitHubManager
from app.services.code_extractor import CodeExtractor

router = APIRouter()

# Initialize services
github_manager = GitHubManager(
    base_path=settings.REPOS_DIR,
    repo_url=settings.GITHUB_REPO,
    branch=settings.GITHUB_BRANCH,
)

# Global cache for extracted variables
_variables_cache: Optional[Dict] = None
_cache_commit_sha: Optional[str] = None


def get_cached_variables(repo_path, current_commit_sha: str) -> Dict:
    """Get variables from cache or extract if cache is stale."""
    global _variables_cache, _cache_commit_sha

    # Return cached data if commit hasn't changed
    if _variables_cache is not None and _cache_commit_sha == current_commit_sha:
        return _variables_cache

    # Extract variables and update cache
    print(f"Extracting variables (commit: {current_commit_sha})...")
    extractor = CodeExtractor(repo_path)
    _variables_cache = extractor.extract_qbi_variables()
    _cache_commit_sha = current_commit_sha
    print(f"Cached {len(_variables_cache)} variables")

    return _variables_cache


@router.get("/", response_model=VariableList)
async def list_variables():
    """
    Get all QBI-related variables.

    Returns complete metadata for all QBI variables with GitHub links.
    """
    try:
        # Ensure repo is cloned and up to date
        repo_path = github_manager.get_repo_path()
        commit_info = github_manager.get_current_commit()

        # Get variables from cache
        variables_dict = get_cached_variables(repo_path, commit_info["full_sha"])

        # Add GitHub URLs to each variable
        variables_list = []
        for var_name, var_data in variables_dict.items():
            # Add GitHub URL for file
            if var_data["file_path"] != "unknown":
                var_data["github_url"] = github_manager.get_file_url(
                    var_data["file_path"]
                )

                # Add GitHub URL for formula lines
                if (
                    var_data["formula_line_start"]
                    and var_data["formula_line_end"]
                ):
                    var_data["formula_github_url"] = (
                        github_manager.get_file_url_with_lines(
                            var_data["file_path"],
                            var_data["formula_line_start"],
                            var_data["formula_line_end"],
                        )
                    )

            variables_list.append(VariableMetadata(**var_data))

        return VariableList(
            variables=variables_list,
            count=len(variables_list),
            commit_sha=commit_info["sha"],
            commit_date=commit_info["date"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{variable_name}", response_model=VariableMetadata)
async def get_variable(variable_name: str):
    """
    Get detailed information about a specific variable.

    Args:
        variable_name: Variable name (e.g., "qualified_business_income")

    Returns:
        Complete variable metadata with GitHub links
    """
    try:
        # Ensure repo is available
        repo_path = github_manager.get_repo_path()
        commit_info = github_manager.get_current_commit()

        # Get variables from cache
        variables_dict = get_cached_variables(repo_path, commit_info["full_sha"])

        if variable_name not in variables_dict:
            raise HTTPException(
                status_code=404, detail=f"Variable '{variable_name}' not found"
            )

        var_data = variables_dict[variable_name]

        # Add GitHub URLs
        if var_data["file_path"] != "unknown":
            var_data["github_url"] = github_manager.get_file_url(var_data["file_path"])

            if var_data["formula_line_start"] and var_data["formula_line_end"]:
                var_data["formula_github_url"] = github_manager.get_file_url_with_lines(
                    var_data["file_path"],
                    var_data["formula_line_start"],
                    var_data["formula_line_end"],
                )

        return VariableMetadata(**var_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/dependency", response_model=VariableGraph)
async def get_dependency_graph():
    """
    Get the complete dependency graph for QBI variables.

    Returns nodes and edges for visualization, with layer assignments.
    """
    try:
        # Ensure repo is available
        repo_path = github_manager.get_repo_path()
        commit_info = github_manager.get_current_commit()

        # Get variables from cache
        variables_dict = get_cached_variables(repo_path, commit_info["full_sha"])

        # Build graph with operation nodes
        nodes = []
        edges = []

        # Create variable nodes
        for var_name, var_data in variables_dict.items():
            # Determine node type
            if var_data["is_input"]:
                node_type = "input"
            elif var_name == "qualified_business_income_deduction":
                node_type = "output"
            else:
                node_type = "intermediate"

            nodes.append(
                {
                    "id": var_name,
                    "label": var_data.get("label", var_name),
                    "type": node_type,
                    "entity": var_data.get("entity"),
                }
            )

            # Add operation nodes for this variable
            for op_node in var_data.get("operation_nodes", []):
                nodes.append({
                    "id": op_node["id"],
                    "label": op_node["label"],
                    "type": op_node["type"],
                    "entity": op_node.get("op_type", ""),
                    "details": op_node.get("details"),
                    "value": op_node.get("value"),
                    "parent_variable": op_node.get("parent_variable"),
                })

            # Add operation edges for this variable
            for op_edge in var_data.get("operation_edges", []):
                edges.append({
                    "source": op_edge["source"],
                    "target": op_edge["target"],
                    "type": op_edge["type"],
                })

        # Create edges from high-level dependencies
        for var_name, var_data in variables_dict.items():
            for dep in var_data["dependencies"]:
                edges.append(
                    {
                        "source": dep,
                        "target": var_name,
                        "type": "dependency",
                    }
                )

            for add_var in var_data["adds"]:
                edges.append(
                    {
                        "source": add_var,
                        "target": var_name,
                        "type": "add",
                    }
                )

        return VariableGraph(nodes=nodes, edges=edges)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_from_github():
    """
    Sync latest changes from GitHub master branch.

    Returns commit information after sync.
    """
    try:
        sync_info = github_manager.sync()
        return {
            "status": "success",
            "message": f"Synced to commit {sync_info['sha']}",
            "commit": sync_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
