#pragma once
// this shim emulates basic Arduino classes/functions
// so that native unit tests can compile and run without Arduino framework

#ifdef __cplusplus
  #include <string>
  #include <chrono>
  #include <thread>

// Minimal replacement for Arduinos String class
// Based on std::string but with Arduino-like constructors and operators
  class String : public std::string {
  public:
    using std::string::string;
    String(const char* s) : std::string(s) {}
    String(long n) : std::string(std::to_string(n)) {}
    const char* c_str() const { return std::string::c_str(); }
    friend String operator+(const String& a, const String& b){return String((a+std::string(b)).c_str());}
    friend String operator+(const String& a, const char* b){return String((a+std::string(b)).c_str());}
    friend String operator+(const char* a, const String& b){return String((std::string(a)+b).c_str());}
  };

  // Replacement for Arduinos delay() – just sleeps on the host system
  inline void delay(unsigned long ms){
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
  }

  // Replacement for Arduinos millis() – returns time since program start
  inline unsigned long millis(){
    using namespace std::chrono;
    static const auto t0 = steady_clock::now();
    return (unsigned long)duration_cast<milliseconds>(steady_clock::now()-t0).count();
  }
#endif
