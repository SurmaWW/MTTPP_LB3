#include <iostream>
#include <cstring>
#include <winsock2.h>
#include <windows.h>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

void run_pipe() {
    int num;
    if (cin >> num) {
        cerr << "[C++ Pipe] Number we got - " << num << endl;
        cout << num << endl;
    }
}

void run_socket() {
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    SOCKET server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));

    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(8080);

    bind(server_fd, (struct sockaddr*)&address, sizeof(address));
    listen(server_fd, 1);

    int addrlen = sizeof(address);
    SOCKET client_fd = accept(server_fd, (struct sockaddr*)&address, &addrlen);

    int num;
    recv(client_fd, (char*)&num, sizeof(num), 0);
    cerr << "[C++ Socket] Number we got - " << num << endl;
    send(client_fd, (const char*)&num, sizeof(num), 0);

    closesocket(client_fd);
    closesocket(server_fd);
    WSACleanup();
}

void run_shared_memory() {
    HANDLE hMapFile = OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, "Local\\MySharedMemBlock");
    if (hMapFile == NULL) {
        cerr << "[C++ SHM] Error" << endl;
        return;
    }

    char* ptr = (char*)MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, 4096);
    if (ptr == NULL) {
        cerr << "[C++ SHM] Error MapViewOfFile!" << endl;
        CloseHandle(hMapFile);
        return;
    }

    // Чекаємо, поки Python встановить прапорець 1
    while (ptr[0] != 1) {
        Sleep(5);
    }

    int num;
    memcpy(&num, ptr + 1, sizeof(num));
    cerr << "[C++ Shared Memory] Number we got - " << num << endl;

    // Говоримо Python, що дані прочитано
    ptr[0] = 2;

    UnmapViewOfFile(ptr);
    CloseHandle(hMapFile);
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    string mode = argv[1];

    if (mode == "pipe") run_pipe();
    else if (mode == "socket") run_socket();
    else if (mode == "shm") run_shared_memory();

    return 0;
}