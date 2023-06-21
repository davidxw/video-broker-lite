import React, { useState, useEffect } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Stack from 'react-bootstrap/Stack';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

const URI = `${window.location.protocol}//${window.location.hostname}`


const textStyle = {
  position: "absolute",
  bottom: -5,
  left: 5,
  color: "white",
  fontSize: "1.5vw",
  backgroundColor: "rgb(0, 0, 0, 0.8)",
  paddingLeft: 3,
  paddingRight: 3,
  borderRadius: 3,
}


// constants
const PORTS = {
  http: { base: "30888", ai: "30889" },
  rtsp: { base: "30554", ai: "30555" }
}

const STREAMS = [{ address: 'cam1', ai: false },
{ address: 'sm1', ai: false },
{ address: 'bw1', ai: false },
{ address: 'inf1', ai: true },
{ address: 'blur1', ai: true }]

const CENTER = 'bw1'

const getStreamList = (streams, center, gotoUri) => {

  if (streams.length === 0) {
    return []
  }

  const ctr_idx = Math.floor((streams.length - 1) / 2)

  return streams.reduce((res, ele, idx) => {

    const port = {
      rtsp: ele.ai ? PORTS.rtsp.ai : PORTS.rtsp.base,
      http: ele.ai ? PORTS.http.ai : PORTS.http.base
    }
    const new_rec = {
      key: ele.address,
      rtsp: `${gotoUri.replace('http:', 'rtsp:')}:${port.rtsp}/${ele.address}`,
      http: `${gotoUri}:${port.http}/${ele.address}`,
      height: ele.address === center ? "500vw" : "250vw",
      width: "100%"
    }

    if (idx < ctr_idx) {
      return ({
        ...res,
        top: res.top.concat(new_rec)
      })
    } else if (idx === ctr_idx) {
      return ({
        ...res,
        center: res.center.concat(new_rec)
      })
    } else {
      return ({
        ...res,
        bottom: res.bottom.concat(new_rec)
      })

    }

  }, { top: [], center: [], bottom: [] })

}


function App() {

  const [gotoUri, setGotoUri] = useState(URI)
  const [streamList, setStreamList] = useState(getStreamList(STREAMS, CENTER, gotoUri))
  const [uri, setUri] = useState(URI)

  const [localMode, setLocalMode] = useState(false)

  useEffect(() => {
    setStreamList(getStreamList(STREAMS, CENTER, gotoUri))
    setLocalMode(gotoUri === "http://localhost")
  }, [gotoUri])

  const handleUriChange = (newUri) => {
    let reworkedUri = newUri

    if (newUri === '') {
      reworkedUri = "http://localhost"
    } else if (!newUri.startsWith("http://")) {
      if (!newUri.startsWith("https://")) {
        reworkedUri = `http://${newUri}`
      }
    }

    if (reworkedUri !== uri) {
      setUri(reworkedUri)
    }

    setGotoUri(reworkedUri)

  }


  console.log(URI)

  return (

    <Container className="p-3">
      <Container className="p-5 mb-4 bg-light rounded-3">
        <Row>
          <Form>
            <Form.Group className="mb-3" controlId="formURL">
              <Row className="justify-content-md-center">
                <Col md="auto">
                  <h1>Real-time Object Detection & Tracking</h1>
                </Col>
              </Row>
              <Row>
                <Form.Label>Server IP address</Form.Label>
              </Row>
              <Stack direction="horizontal" gap={1}>
                <Col >
                  <Form.Control type="uri" placeholder="Enter server IP address" value={uri} onChange={(ev) => setUri(ev.target.value)} />
                </Col>
                <Col md="auto" >
                  <Button variant="primary" onClick={() => handleUriChange(uri)} >
                    Go
                  </Button>
                </Col>

              </Stack>
            </Form.Group>
          </Form>
        </Row>
        <Row className="justify-content-md-center">
          {
            localMode
              ?
              <div>
                <p>You are in local mode.</p>
                <p>Enter a valid Video Broker IP on the line above and clic "go"</p>
              </div>
              :
              <Container>
                <Row className="justify-content-md-center">
                  {streamList.top.map((ele) =>
                  (
                    <Col id={ele.address} style={{ position: "relative" }}>
                      <a href={ele.rtsp} style={textStyle}>{ele.rtsp}</a>
                      <iframe title="cam1" width={ele.width} height={ele.height} className="VideoFrame" src={ele.http} />
                    </Col>)
                  )}
                </Row>
                <Row className="justify-content-md-center">
                  {streamList.center.map((ele) =>
                  (
                    <Col id={ele.address} style={{ position: "relative" }}>
                      <a href={ele.rtsp} style={textStyle}>{ele.rtsp}</a>
                      <iframe title="cam1" width={ele.width} height={ele.height} className="VideoFrame" src={ele.http} />
                    </Col>)
                  )}
                </Row>
                <Row className="justify-content-md-center">
                  {streamList.bottom.map((ele) =>
                  (
                    <Col id={ele.address} style={{ position: "relative" }}>
                      <a href={ele.rtsp} style={textStyle}>{ele.rtsp}</a>
                      <iframe title="cam1" width={ele.width} height={ele.height} className="VideoFrame" src={ele.http} />
                    </Col>)
                  )}
                </Row>
              </Container>
          }
        </Row>
      </Container>
    </Container>

  );
}

export default App;
