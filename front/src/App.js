import {createBrowserRouter, RouterProvider, useNavigate} from "react-router-dom";
import {Navbar} from "./Navbar";
import {WelcomePage} from "./pages/WelcomePage";
import {ModelCreationPage} from "./pages/ModelCreationPage";
import {LoginPage} from "./pages/LoginPage";
import {SignUpPage} from "./pages/SignUpPage";
import {useEffect, useState} from "react";
import Cookies from 'js-cookie';
import axios from 'axios';
import {ModelTuningPage} from "./pages/ModelTuningPage";






const App = () => {
    const [isUser, setIsUser] = useState(!!Cookies.get('user_email'));
    const [userModels, setUserModels] = useState();
    const [modelSearch, setModelSearch] = useState("")

    useEffect(() => {
        let config = {
            method: 'get',
            maxBodyLength: Infinity,
            url: 'http://178.20.40.246:8888/get_user_models?email=' + encodeURI(Cookies.get("user_email")),
            headers: { }
        };

        axios.request(config)
            .then((response) => {
                setUserModels(response.data);
            })
            .catch((error) => {
                console.log(error);
            });
    }, [])

    const router = createBrowserRouter([
        {
            path: "/",
            element: <section className="app">
                <Navbar isUser={isUser} setIsUser={setIsUser} userModels={userModels} modelSearch={modelSearch} setUserModels={setUserModels}/>
                <WelcomePage setModelSearch={setModelSearch}/>
            </section>,
        },
        {
            path: "/create",
            element: <section className="app">
                <Navbar isUser={isUser} setIsUser={setIsUser} userModels={userModels} modelSearch={modelSearch} setUserModels={setUserModels}/>
                <ModelCreationPage />
            </section>,
        },
        {
            path: "/fine-tune",
            element: <section className="app">
                <Navbar isUser={isUser} setIsUser={setIsUser} userModels={userModels} modelSearch={modelSearch} setUserModels={setUserModels}/>
                <ModelTuningPage />
            </section>,
        },
        {
            path: "/login",
            element: <section className="app">
                <Navbar isUser={isUser} setIsUser={setIsUser} userModels={userModels} modelSearch={modelSearch} setUserModels={setUserModels}/>
                <LoginPage isUser={isUser} setIsUser={setIsUser} setUserModels={setUserModels}/>
            </section>,
        },
        {
            path: "/signup",
            element: <section className="app">
                <Navbar isUser={isUser} setIsUser={setIsUser} userModels={userModels} modelSearch={modelSearch} setUserModels={setUserModels}/>
                <SignUpPage setIsUser={setIsUser} setUserModels={setUserModels}/>
            </section>,
        },
    ]);

    return <RouterProvider router={router} />
}

export {App}