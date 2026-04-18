FROM node:18-alpine

# Install FFmpeg (required for video duration and audio extraction)
RUN apk add --no-cache ffmpeg

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./
RUN npm install --production

# Bundle app source
COPY . .

# Ensure uploads directory exists
RUN mkdir -p uploads

# Expose port
EXPOSE 3000

# Start command
CMD [ "node", "server.js" ]
