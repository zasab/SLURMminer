import http from "./helper/http";

export default new class logService {
    upload(file) {
        return http.post("/create_exe_file_locally", file, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
    }

    run(arr) {
        return http.post("/run_exe_file", { exe_file_content: arr })
    }

}

