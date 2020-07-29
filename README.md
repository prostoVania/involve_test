# involve_test
Test task for Involve

Deploy locally:
```
git clone https://github.com/prostoVania/involve_test.git
cd involve
docker build -t involve-kalishuk:latest .
docker run -d -p 5000:5000 involve-kalishuk
```