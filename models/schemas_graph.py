from pydantic import BaseModel, Field


class GraphNodeItem(BaseModel):
    vid: str = Field(..., description="Node unique id")
    properties: dict = Field(default_factory=dict, description="Node properties")


class AddNodesPayload(BaseModel):
    tag: str = Field(..., description="Node tag, e.g. Character")
    nodes: list[GraphNodeItem] = Field(..., description="Node list")


class GraphEdgeItem(BaseModel):
    source_vid: str = Field(..., description="Source node vid")
    target_vid: str = Field(..., description="Target node vid")
    properties: dict = Field(default_factory=dict, description="Edge properties")


class AddEdgesPayload(BaseModel):
    edge_type: str = Field(..., description="Edge type, e.g. Character_to_Character")
    edges: list[GraphEdgeItem] = Field(..., description="Edge list")


class DeleteNodesPayload(BaseModel):
    vids: list[str] = Field(..., description="Node vids to delete")
    cascade: bool = Field(default=True, description="Delete connected edges together")


class GraphEdgeRef(BaseModel):
    source_vid: str = Field(..., description="Source node vid")
    target_vid: str = Field(..., description="Target node vid")


class DeleteEdgesPayload(BaseModel):
    edge_type: str = Field(..., description="Edge type, e.g. Character_to_Character")
    edges: list[GraphEdgeRef] = Field(..., description="Edge refs to delete")