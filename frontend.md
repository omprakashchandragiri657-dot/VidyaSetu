# Frontend Access Links for Smart Student Hub

The frontend React app is accessible at the following URLs when running locally:

- Login Page: http://localhost:3000/login
- Register Page: http://localhost:3000/register
- Dashboard (after login): http://localhost:3000/dashboard
- Student Portal (achievement submission): http://localhost:3000/student-portal

Make sure the backend Django server is running at http://127.0.0.1:8000/ for API access.

If you see the default React start page ("Edit src/App.js and save to reload."), please ensure you have started the React app correctly with the implemented source code and that the build is up to date.

To start the frontend development server, run:
```
cd frontend/webapp
npm start
```

To build the frontend for production, run:
```
npm run build
```

Then serve the build folder using a static server, for example:
```
npm install -g serve
serve -s build
```

This will serve the production build on a local port.

Please let me know if you need assistance with running or deploying the frontend.
