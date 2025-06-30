document.getElementById('bttnTambahProduk').addEventListener('click', async () => {
  // Contoh data produk baru yang ingin ditambahkan via JSON
  const produkBaru = {
    name: "Lipstick Pinky",
    price: 75000,
    description: "Lipstick warna pink cantik dan tahan lama",
    // Biasanya image diupload via form, kalau lewat API bisa jadi URL image atau base64
    // Sesuaikan dengan API backendmu
  };

  try {
    const response = await fetch('/api/add-product', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(produkBaru)
    });

    if (!response.ok) {
      throw new Error('Gagal menambahkan produk');
    }

    const data = await response.json();
    alert('Produk berhasil ditambahkan: ' + data.name);

    // Opsional: refresh halaman atau update tabel produk secara dinamis

  } catch (error) {
    alert(error.message);
  }
});
