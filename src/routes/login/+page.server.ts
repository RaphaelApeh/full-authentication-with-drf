

const actions = {
    default: async ({request}: any) => {
        let data = await request.FormData();
        console.log(data)
    }
}