"""
Point history API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional

from app.services.point_history_service import PointHistoryService
from app.models.point_history import (
    PointDetails,
    PointHistoryFilter,
    PointOutcome
)
from app.core.auth import get_current_user
from app.models.user import UserInDB as User

router = APIRouter(prefix="/point-history", tags=["point-history"])


@router.post("/points", status_code=status.HTTP_201_CREATED)
async def create_point(
    point: PointDetails,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new point record

    Records detailed information about a point including:
    - Set/game/point numbers
    - Score before and after
    - Server, receiver, winner
    - Outcome (ACE, WINNER, UNFORCED_ERROR, etc.)
    - Rally length and duration
    - Serve details
    - Critical flags (break point, set point, match point)
    """
    service = PointHistoryService()

    try:
        created_point = await service.create_point(point)
        return {
            "message": "Point created successfully",
            "point_id": created_point.point_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create point: {str(e)}"
        )


@router.get("/points/{point_id}")
async def get_point(
    point_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get point by ID"""
    service = PointHistoryService()

    try:
        point = await service.get_point(point_id)
        if not point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Point not found: {point_id}"
            )
        return point
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get point: {str(e)}"
        )


@router.get("/matches/{match_id}/points")
async def get_points_by_match(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all points for a match

    Returns points ordered by occurrence (set → game → point)
    """
    service = PointHistoryService()

    try:
        points = await service.get_points_by_match(match_id)
        return {
            "match_id": match_id,
            "total_points": len(points),
            "points": points
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get points: {str(e)}"
        )


@router.get("/matches/{match_id}/players/{player_id}/points")
async def get_points_by_player(
    match_id: str,
    player_id: str,
    won_only: bool = Query(False, description="Only return points won by player"),
    current_user: User = Depends(get_current_user)
):
    """
    Get points for a specific player

    Query params:
    - won_only: If true, only return points won by player
    """
    service = PointHistoryService()

    try:
        points = await service.get_points_by_player(
            match_id=match_id,
            player_id=player_id,
            won_only=won_only
        )
        return {
            "match_id": match_id,
            "player_id": player_id,
            "won_only": won_only,
            "total_points": len(points),
            "points": points
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get player points: {str(e)}"
        )


@router.get("/matches/{match_id}/sets/{set_number}/points")
async def get_points_by_set(
    match_id: str,
    set_number: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get all points for a specific set

    Args:
    - set_number: Set number (1-5)
    """
    service = PointHistoryService()

    try:
        points = await service.get_points_by_set(match_id, set_number)
        return {
            "match_id": match_id,
            "set_number": set_number,
            "total_points": len(points),
            "points": points
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get set points: {str(e)}"
        )


@router.get("/matches/{match_id}/break-points")
async def get_break_points(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all break points for analysis of critical moments

    Returns all points where is_break_point=True
    Useful for analyzing clutch performance
    """
    service = PointHistoryService()

    try:
        points = await service.get_break_points(match_id)
        return {
            "match_id": match_id,
            "total_break_points": len(points),
            "break_points": points
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get break points: {str(e)}"
        )


@router.get("/matches/{match_id}/points/by-outcome/{outcome}")
async def get_points_by_outcome(
    match_id: str,
    outcome: PointOutcome,
    current_user: User = Depends(get_current_user)
):
    """
    Get points by outcome type

    Outcomes:
    - ACE, WINNER, UNFORCED_ERROR, FORCED_ERROR
    - DOUBLE_FAULT, SERVICE_WINNER, RETURN_WINNER
    - VOLLEY_WINNER, SMASH_WINNER, DROP_SHOT_WINNER
    - LET, NET, OUT, LONG, WIDE
    """
    service = PointHistoryService()

    try:
        points = await service.get_points_by_outcome(match_id, outcome)
        return {
            "match_id": match_id,
            "outcome": outcome.value,
            "total_points": len(points),
            "points": points
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get points by outcome: {str(e)}"
        )


@router.post("/points/query")
async def query_points(
    filter: PointHistoryFilter,
    current_user: User = Depends(get_current_user)
):
    """
    Query points with complex filters

    Filter options:
    - match_id: Filter by match
    - player_id: Filter by player (server, receiver, or winner)
    - set_number: Filter by set
    - outcome: Filter by outcome type
    - is_break_point: Filter break points
    - is_set_point: Filter set points
    - is_match_point: Filter match points
    - min_rally_length: Minimum rally length
    - max_rally_length: Maximum rally length
    """
    service = PointHistoryService()

    try:
        points = await service.query_points(filter)
        return {
            "filter": filter.model_dump(exclude_none=True),
            "total_points": len(points),
            "points": points
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query points: {str(e)}"
        )


@router.get("/matches/{match_id}/summary")
async def get_match_summary(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get match summary statistics

    Returns:
    - Total points
    - Points by outcome (breakdown)
    - Average rally length
    - Break points (total and converted)
    - Aces, double faults, winners, unforced errors counts
    """
    service = PointHistoryService()

    try:
        summary = await service.get_match_summary(match_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match summary: {str(e)}"
        )


@router.delete("/matches/{match_id}/points", status_code=status.HTTP_200_OK)
async def delete_match_points(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete all points for a match"""
    service = PointHistoryService()

    try:
        deleted_count = await service.delete_match_points(match_id)
        return {
            "message": f"Deleted {deleted_count} points for match {match_id}",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete points: {str(e)}"
        )
