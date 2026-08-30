


# Adjust the import path as needed based on your project structure
from satellite_service import SatelliteService

if __name__ == "__main__":
    service = SatelliteService()
    sat = service.create_satellite(
        norad_id=25544,
        
        name="ISS (ZARYA)",
        tle0="ISS (ZARYA)",
        tle1="1 25544U 98067A   21275.51837963  .00001264  00000-0  29621-4 0  9995",
        tle2="2 25544  51.6439  48.3240 0003706  65.2369  43.2148 15.48815336298327",
        epoch="2021-10-02T12:00:00Z",
        start="2021-10-02T12:00:00Z",
        end="2021-10-02T13:00:00Z",
        frequency=145.8e6,
        bandwidth=25e3,
        polarization="RHCP",
        power=10.0
    )

    print(sat)
