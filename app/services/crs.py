import geopandas as gpd


def get_projected_geodataframe(
    gdf: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, str | None]:

    if gdf.crs is None:
        raise ValueError(
            "Input file does not contain a CRS. "
            "Cannot safely calculate measurements."
        )

    source_crs = gdf.crs

    if not source_crs.is_geographic:
        return gdf, source_crs.to_string()

    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError("Unable to determine a suitable projected CRS.")

    projected_gdf = gdf.to_crs(projected_crs)

    return projected_gdf, projected_crs.to_string()