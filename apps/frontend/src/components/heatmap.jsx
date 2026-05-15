"use client";

import "../App.css"
import "@/index.css" // Ensure base classes are present if needed
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Marker, Popup, Polygon } from 'react-leaflet'

export function Heatmap({ convertedConjs }) {

    const purpleOptions = { color: 'purple' }

    function invertCoordinates(coordinates) {
        return coordinates.map(([x, y]) => [
            y,
            x
        ]);
    } 

    function mappedPolygons(conj) {
        if (conj.coordinates) {
            let coordinates = conj.coordinates
            coordinates = invertCoordinates(coordinates)
            return (
                <Polygon pathOptions={purpleOptions} positions={coordinates} />
            )
        }

        return (<></>)
    }

    function getCoordinateCenter(conjArray) {
        if(conjArray)
        {
            let conj = conjArray[0]
            if(conj.coordinates)
            {
                let firstCoordinate = [conj.coordinates[0][1], conj.coordinates[0][0]]
                return firstCoordinate
            }
            return [51.505, -0.09]
        }
        
    }

    return (
        <>
        {convertedConjs[0].coordinates && (
            <MapContainer center={getCoordinateCenter(convertedConjs)} zoom={13} scrollWheelZoom={true}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={[51.505, -0.09]}>
                    <Popup>
                        A pretty CSS3 popup. <br /> Easily customizable.
                    </Popup>
                </Marker>

                {convertedConjs.map(mappedPolygons)}
            </MapContainer>
        )}
            
        </>
    )
}