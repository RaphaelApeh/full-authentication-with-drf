
const logoutUrl = `${location.origin}/api/logout/`
const csrf = document.currentScript.dataset.csrf


document.addEventListener("DOMContentLoaded", function(){
    
    if (localStorage.getItem("token") === undefined){
        this.location.href = "/login/"
    }else if (!localStorage.getItem("token")){
        this.location.pathname = "/login/"
    }
    
    if (location.pathname === "/"){
        fetch(`${this.location.origin}/api/user/`, {
            method: "GET",
            headers: {
                "Authorization": `token ${localStorage.getItem("token")}`
            }
        }).then(response=> response.json()
        )
        .then(data=> document.querySelector("#result").innerHTML = data["username"]) 
    }
    // Logout route
    if (this.location.pathname === "/logout/"){
        document.querySelector("form").addEventListener("submit", (e)=> {
            e.preventDefault()
            fetch(logoutUrl, {
                method: "POST",
                headers: {
                    "ContentType": "application/json",
                    "Authorization": `Token ${localStorage.getItem("token")}`,
                    "X-CSRFToken": csrf
                }
            }).then(response=> response.json())
            .then(data=> console.log(JSON.stringify(data)))
            localStorage.removeItem("token")
            this.location.pathname = "/login/"
        })
    }
    
})