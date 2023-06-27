FROM aler9/rtsp-simple-server:v0.19.3 AS rtsp
FROM alpine:3.12

# Add ffmpeg
RUN apk add --no-cache ffmpeg

# Copy over rtsp-simple-server and server config
COPY --from=rtsp /rtsp-simple-server /

EXPOSE 1935 8554 8888 8889

COPY rtsp-simple-server.yml /


ENTRYPOINT [ "/rtsp-simple-server" ]