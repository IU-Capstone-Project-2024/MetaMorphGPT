import {createBrowserRouter, RouterProvider} from "react-router-dom";
import {Navbar} from "./Navbar";
import {WelcomePage} from "./WelcomePage";
import {ModelCreationPage} from "./ModelCreationPage";
import {useState} from "react";

const router = createBrowserRouter([
    {
        path: "/",
        element: <section className="app">
            <Navbar />
            <WelcomePage />
        </section>,
    },
    {
        path: "/create",
        element: <section className="app">
            <Navbar />
            <ModelCreationPage />
        </section>,
    },
]);

const App = () => {
    return <RouterProvider router={router} />
}

export {App}