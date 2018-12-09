'use strict'

function GoogleMap(payload) {
    this.el = null

    this.style = [{
        'featureType': 'water',
        'elementType': 'geometry',
        'stylers': [{
            'color': '#222222'
        }]
    }, {
        'featureType': 'landscape',
        'stylers': [{
            'color': '#000000'
        }]
    }, {
        'featureType': 'transit',
        'stylers': [{
            'visibility': 'off'
        }]
    }, {
        'featureType': 'road',
        'stylers': [{
            'visibility': 'off'
        }]
    }, {
        'featureType': 'poi',
        'stylers': [{
            'visibility': 'off'
        }]
    }, {
        'featureType': 'administrative',
        'stylers': [{
            'visibility': 'off'
        }]
    }, {
        'featureType': 'water',
        'elementType': 'labels.text.fill',
        'stylers': [{
            'visibility': 'on'
        }, {
            'color': '#333333'
        }]
    }, {
        'featureType': 'landscape',
        'elementType': 'labels',
        'stylers': [{
            'color': '#dadada'
        }, {
            'visibility': 'simplified'
        }]
    }, {
        'featureType': 'road',
        'elementType': 'geometry.stroke',
        'stylers': [{
            'visibility': 'on'
        }, {
            'weight': 0.1
        }, {
            'color': '#111111'
        }]
    }, {
        'elementType': 'labels.text.stroke',
        'stylers': [{
            'visibility': 'off'
        }]
    }]

    this.install = function() {
        const element = document.getElementById('map')
        setTimeout(() => {
            this.load(element, payload)
        }, 500)
    }

    this.load = function(element, locations) {
        const map = new google.maps.Map(document.getElementById('map'), {
            center: locations[0].coordinates,
            zoom: 3.5,
            disableDefaultUI: true
        });

        map.set('styles', this.style)

        const path = new google.maps.Polyline({
            path: locations.map(x => x.coordinates),
            geodesic: true,
            strokeColor: '#F2F2F2',
            strokeOpacity: 0.3,
            strokeWeight: 1.5
        })
        path.setMap(map)

        for (const id in locations) {
            addMarker(map, locations[id])
        }
    }

    function addMarker(map, location, icon = {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 3,
        strokeWeight: 0,
        fillOpacity: 1,
        fillColor: 'white'
    }) {

        const contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">' + location.location + '</h1>'+
            '<div id="bodyContent">'+
            '<p>(' + location.date + ') ' + location.purpose + '</p>'+
            '</div>'+
            '</div>';
        const info = new google.maps.InfoWindow({
          content: contentString
        })
        const marker = new google.maps.Marker({
            position: location.coordinates,
            icon: icon,
            draggable: false,
            map: map,
            title: location.location
        })
        marker.addListener('click', function() {
          info.open(map, marker);
        });
    }
}
