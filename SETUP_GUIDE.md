# DealScout one-click setup

## Requirements

Install **Docker Desktop** on Windows, macOS, or Linux. Docker runs the frontend, backend, and MongoDB together, so Python, Node.js, and MongoDB do not need separate installation.

## Windows

1. Extract the DealScout project folder.
2. Start Docker Desktop.
3. Double-click `setup.bat`.
4. Open `http://localhost:3000`.

## macOS / Linux

1. Extract the project and start Docker.
2. Open Terminal in the DealScout folder.
3. Run `chmod +x setup.sh && ./setup.sh`.
4. Open `http://localhost:3000`.

## Optional live shopping results

Create a `.env` file beside `docker-compose.yml` containing `SERPAPI_KEY=your_key`, then run the setup script again. Without this key, Demo Catalog remains fully usable and Live mode is explicitly labelled as preview data.

## Stop or reset

- Stop: `docker compose down`
- Start again: `docker compose up -d`
- Delete all stored searches: `docker compose down -v`

## Login

- Email: `preview@dealscout.local`
- Password: `dealscout123`