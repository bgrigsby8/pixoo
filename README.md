# Pixoo Meeting Director

A Viam module that integrates Google Calendar with a Pixoo display device to provide smart meeting room navigation. The system uses face detection to identify when someone is present and displays directional arrows on the Pixoo screen to guide them to their next meeting location.

## Features

- **Google Calendar Integration**: Automatically fetches upcoming meetings from Google Calendar
- **Face Detection**: Uses camera input with face detection to determine when to activate the display
- **Smart Display**: Shows directional arrows and meeting information on Pixoo LED display
- **Background Monitoring**: Continuously monitors for upcoming events every 60 seconds
- **Room Path Mapping**: Configurable room-to-room navigation paths

## Model brad-grigsby:pixoo:meeting-director

A sensor component that combines camera input, face detection, Google Calendar API, and Pixoo display control to create an intelligent meeting room director system.

### Configuration

```json
{
  "camera_name": "string",
  "pixoo_ip": "string", 
  "face_detector": "string",
  "path_emails": {"string": "string"}
}
```

#### Attributes

| Name            | Type            | Inclusion | Description                                    |
|-----------------|-----------------|-----------|------------------------------------------------|
| `camera_name`   | string          | Required  | Name of the camera component for face detection |
| `pixoo_ip`      | string          | Required  | IP address of the Pixoo display device         |
| `face_detector` | string          | Required  | Name of the vision service for face detection  |
| `path_emails`   | object (string→string) | Required  | Dictionary mapping person names to email addresses |

#### Example Configuration

```json
{
  "camera_name": "my-camera",
  "pixoo_ip": "192.168.1.100",
  "face_detector": "face-detector-service", 
  "path_emails": {
    "john_doe": "john.doe@company.com",
    "jane_smith": "jane.smith@company.com"
  }
}
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure Google Calendar API credentials
3. Set up your Pixoo device on the network
4. Configure room paths in `src/models/config.py`
5. Run with: `./run.sh`

## Dependencies

- Google Calendar API (google-api-python-client, google-auth)
- Pixoo Python library
- Viam SDK (0.50.0)
- Computer vision for face detection
